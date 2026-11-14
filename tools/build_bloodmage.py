#!/usr/bin/env python3
"""Author the Bloodmage: ability kit + four talent trees.

    PYTHONPATH=. python3 tools/build_bloodmage.py [--apply]

Bloodmage is the CoA class that pays for its magic in blood. It had stats,
armour (leather), weapons (dagger / 1h sword / staff) and a resource pair
already defined, and nothing else. Identity per the reference:

  Sanguine     RANGED DPS    "Affliction Warlock crossed with a Blood DK
                             personal-survival layer." Shadow DoTs, health-cost
                             nukes, Thirst dumped into a lifesteal fang.
  Accursed     MELEE/RANGED  "Feral/Guardian Druid's form-dancing bolted onto
                             a Blood DK self-sustain layer." Bolts at range,
                             a lifestealing bruiser in Accursed Form.
  Eternal      TANK          "Guardian Druid / Blood Death Knight hybrid."
                             Eternal Curse trades damage for armour, Stamina
                             and threat; it heals through its own output.
  Fleshweaver  RANGED/SUPPORT"Discipline Priest, with a dash of Blood DK."
                             Builds Rage by paying health, spends it on
                             shields and instants, damages and heals at once.

SOURCE. reference/coa_sidekick/CLASS_bloodmage.txt, the four
SPEC_bloodmage__*.txt pages and reference/coa_sidekick/talents/bloodmage.json,
captured from ascensionsidekick.com. Every ability and talent name below is a
real CoA name off those pages, with one flagged exception (Blood Rite - see
its _source).

RESOURCE MODEL, and the one thing worth reading before the numbers.
CLASS_RESOURCE_MAP gives Bloodmage (RAGE, VITALITY). Rage is the primary pool
(0-100, Character.max_rage) and Vitality is a dict-backed secondary, also
0-100. The important engine fact is that Bloodmage gets NO Rage for free:
Character.generates_rage_from_combat() is True only for Warriors and for
Rage-form shapeshifters, and restore_resources_between_turns() regenerates
Energy and Mana but never Rage. So a Bloodmage that only spent Rage would be
unable to act.

That lines up exactly with what the reference describes - "you live in caster
form spending your own health bar to cast", "your caster-form casts are Rage
builders, not filler" - so the kit is built as a three-currency loop:

  health  -> the blood spells (Bloodbolt, Veinburst, Rotclaw, Blood Tap, ...)
             cost HP and `generates` Rage or Vitality. Spending health is
             never lethal: Ability._has_resource requires current_health >
             cost outright.
  rage    -> every payoff, heal, shield and defensive. Flat cost across
             ranks, 15-45, against ~20 Rage per builder cast, so one or two
             builders fund one payoff. A cost over 100 would be uncastable
             forever, which validate_class.py fails on.
  vitality-> banked by Bloodmoon Blast and Gorge, spent by Vampiric Fang.
             This is CoA's Thirst / Pooled Vitality shape: health-cost casts
             stack it and a signature ability consumes the stack.

Health costs are the one place these ranks do NOT hold cost flat. An
unequipped Bloodmage has 196 health at level 1 and 436 at level 60, so a flat
cost that is a real 6% bite at level 1 is 2% at the cap and the class stops
feeling like it pays for anything. Health costs therefore scale with rank on
roughly the health curve (e.g. 10 -> 26 over nine ranks), which keeps the
percentage constant. The flat-cost rule still applies in full to Rage and
Vitality, whose pools are fixed at 100.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference is a fan-made planning tool
whose own disclaimer says COA is pre-meta. Damage curves copy the shipped
shapes: warlock.json's shadow_bolt/corruption curve for the Shadow nukes and
DoTs (44 -> 132 over 9 ranks at levels 1/6/12/18/24/32/40/48/56), rogue.json's
flat-cost melee curve for the strikes, cultist.json's hybrid striker for the
mixed spell/melee specs.

Talent effect keys are restricted to ones the engine actually reads, verified
with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. Four mechanics in the reference have no engine hook
and are recorded at the node that carries them:

  Shapeshifting. Accursed Form, Eternal Curse and Blood Curse are real form
  swaps in CoA, and the engine HAS a shapeshift effect_type - but combat/
  forms.py gates every form on form["class"] == char_class and defines none
  for Bloodmage, so a shapeshift ability would silently fail. All three ship
  as persistent self-buffs sharing one exclusive_group, the same way
  Guardian's Formations do.
  Summons. Animated Blood's amalgams and Call of the Darkwing's Shadow Bats
  need pet templates that combat/pet_templates.py does not have, so the
  nodes that scale them were not selected. Nothing summons.
  Interrupts. The engine has no cast-interrupt or school-lock. Aneurysm and
  Arterial Bind use is_stun, the same substitution rogue.json's Kick already
  documents for itself.
  Party-facing talent effects. A talent's effects dict only ever modifies its
  own owner, so CoA's "+3% spell haste to all party and raid members" nodes
  land as the self half only. The party halves that matter are abilities
  instead (Blood-Cursed Armor, Shadow Howl, Bloodthorns), where buff_scope
  works.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Warlock/Rogue's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def _levels(start, count):
    """Rank unlock levels, spaced to stay at or below 58 at the cap."""
    if start == 1:
        return RANK_LEVELS[:count]
    span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
    return [min(58, start + i * span) for i in range(count)]


def ranks(base, step, cost, start=1, count=9, cost_step=0,
          heal=None, heal_step=0, restore=None, restore_step=0):
    """Rank table on the shipped schedule, starting at `start`.

    cost_step is zero for Rage and Vitality - those pools are fixed at 100
    and a scaling cost would eventually make the ability uncastable. It is
    nonzero only for health costs, which track a growing health pool (see
    the module docstring).

    heal/heal_step fill the per-rank heal_value that effect_type
    "damage_and_heal" reads; restore/restore_step fill mana_restore_pct,
    which is what "restore_resource" reads as "% of the named pool".
    """
    out = []
    for i, level in enumerate(_levels(start, count)):
        rank = {"rank": i + 1, "level_req": level,
                "cost": int(round(cost + cost_step * i)),
                "effect_value": int(round(base + step * i))}
        if heal is not None:
            rank["heal_value"] = int(round(heal + heal_step * i))
        if restore is not None:
            rank["mana_restore_pct"] = int(round(restore + restore_step * i))
        out.append(rank)
    return out


def one(level, cost, value=0, **extra):
    """Single-rank table, for cooldowns and stances that do not scale."""
    rank = {"rank": 1, "level_req": level, "cost": cost, "effect_value": value}
    rank.update(extra)
    return [rank]


def ability(aid, name, effect_type, description, rank_table, *, resource="rage",
            cooldown=0, duration=0, stat_mods=None, icon=None, source=None,
            **extra):
    out = {
        "ability_id": f"bloodmage_{aid}",
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


#: Every Cursed Form shares one slot. CoA lets you hold exactly one curse at
#: a time and the whole Accursed/Eternal identity is choosing which.
CURSE = "bloodmage_curse"

#: Shadow is the class's school almost everywhere. Named once so a future
#: retune cannot leave half the kit on a different school by accident.
SHADOW = "shadow"


# ============================================================== ability kit
# Order is roughly the order a player meets them: class kit first, then the
# four specs in the order the reference lists them.
ABILITIES = [
    # ------------------------------------------------------------ class kit
    ability("attack", "Attack", "damage",
            "A measured strike with your weapon.", one(1, 0, 0),
            icon=None,
            source="Convention: every class ships a free rank-1 Attack. It "
                   "is also what a talent's extra_attack proc re-invokes, by "
                   "the <class_prefix>_attack naming rule."),

    ability("bloodbolt", "Bloodbolt", "spell_damage",
            "Open a vein and throw what comes out. It costs you a little "
            "health and leaves you angrier than you were.",
            ranks(44, 11, 10, cost_step=2), resource="health",
            damage_school=SHADOW, generates={"resource": "rage", "amount": 20},
            source="CoA names Bloodbolt in all four spec rotations - the one "
                   "button every Bloodmage presses. The class's Rage engine: "
                   "'your caster-form casts are Rage builders, not filler. "
                   "They fund the free transformed spam.' Warlock's "
                   "shadow_bolt damage curve."),
    ability("bloodmoon_blast", "Bloodmoon Blast", "spell_damage",
            "A slower, heavier pull on your own blood that leaves you "
            "thirsty for someone else's.",
            ranks(50, 13, 12, start=6, count=8, cost_step=2),
            resource="health", damage_school=SHADOW,
            generates={"resource": "vitality", "amount": 12},
            source="CoA: 'Bloodmoon Blast as the main filler to build Thirst "
                   "and Rage'. The engine's `generates` block names one "
                   "resource, so the pair is split: Bloodbolt banks Rage and "
                   "Bloodmoon Blast banks Vitality (CoA's Thirst)."),
    ability("blood_tap", "Blood Tap", "restore_resource",
            "Open a wrist and let the anger in.",
            ranks(0, 0, 16, start=10, count=5, cost_step=4,
                  restore=26, restore_step=3),
            resource="health", cooldown=2, target_type="self",
            restore_resource_type="rage",
            source="CoA: Fleshweaver 'builds it in caster form by paying your "
                   "own health to cast; Blood Tap and your other health-cost "
                   "spells'. restore_resource reads mana_restore_pct as a "
                   "percentage of the NAMED pool, so the rank table carries "
                   "it; warlock_life_tap is the same shape in reverse."),

    ability("fleshcraft", "Fleshcraft", "heal",
            "Mend blood and bone. Whoever you do it to will not want it done "
            "again for a while.",
            ranks(210, 58, 40, start=14, count=6), cooldown=10,
            target_type="ally",
            source="CoA class kit: 'Mend blood and bone, healing an ally for "
                   "50% of their maximum health and applies Sated.' A "
                   "percent-of-max-health heal has no engine hook - heals are "
                   "flat plus healing power - so this is a large flat heal on "
                   "a long cooldown. Sated has no hook either; the cooldown "
                   "is what stops it being spammed."),
    ability("blood_pact", "Blood Pact", "buff",
            "Trade some blood for reflexes you did not have a moment ago.",
            one(12, 20), resource="health", cooldown=8, duration=3,
            stat_mods={"dodge": 15.0, "parry": 5.0}, target_type="self",
            buff_scope="combat",
            source="CoA: 'exchanging health for enhanced reflexes, increasing "
                   "your chance to dodge and reducing the chance for ranged "
                   "attacks to hit you by 50%'. There is no ranged-specific "
                   "avoidance stat, so the ranged half lands as parry."),
    ability("liquify", "Liquify", "buff",
            "Come apart into a puddle. Very little can hurt a puddle.",
            one(26, 25), cooldown=12, duration=2,
            stat_mods={"damage_taken_pct": -0.6}, target_type="self",
            buff_scope="combat",
            source="CoA: 'immune to damage from spells and attacks, but "
                   "preventing you from attacking or casting spells'. Full "
                   "immunity plus a self-silence is not expressible, so this "
                   "is a very large damage reduction with no downside - "
                   "deliberately short and on a long cooldown to pay for the "
                   "half the engine cannot charge you for."),
    ability("shadow_howl", "Shadow Howl", "buff",
            "A howl that gets your allies' feet moving again.",
            one(22, 25), cooldown=10, duration=2,
            stat_mods={"cc_immune": 1}, target_type="self", buff_scope="party",
            source="CoA: 'granting immunity to movement impairing effects to "
                   "all allies for 6 seconds'. cc_immune is the engine's one "
                   "incapacitate immunity, checked in apply_status_effect."),
    ability("wicked_howl", "Wicked Howl", "buff",
            "You get bigger. It is not pleasant to watch.",
            one(28, 20), cooldown=12, duration=3,
            stat_mods={"max_health_pct": 0.25}, target_type="self",
            buff_scope="combat",
            source="CoA: 'increasing your maximum health by 30% for 20 "
                   "seconds'. NOTE max_health_pct is a FRACTION here - "
                   "health * (1.0 + value) - not percent points like "
                   "armor_pct, in an ability's stat_mods exactly as in a "
                   "talent's effects."),
    ability("hemostasis", "Hemostasis", "debuff",
            "Trap something in a sphere of its own blood and leave it there.",
            one(18, 20), cooldown=6, duration=2, target_type="enemy",
            is_stun=True, buff_scope="combat",
            source="CoA: 'Trap an enemy in a blood orb, horrifying them in "
                   "place for 4 seconds.' Named in Sanguine's and Accursed's "
                   "weaknesses as the class-kit control pick."),
    ability("lunge", "Lunge", "damage",
            "Cover the ground between you in one unpleasant movement.",
            ranks(46, 12, 15, start=8, count=7), cooldown=3,
            target_type="enemy", icon=None,
            source="CoA's class tree points at Lunge from three directions - "
                   "Bloodleaper cuts its cooldown, Dark Intent heals you when "
                   "you use it, Cruel Intent adds auto attacks to it - so the "
                   "ability itself has to exist."),
    ability("scarlet_delirium", "Scarlet Delirium", "spell_dot",
            "Show them what is under their own skin. They stop being able to "
            "think about anything else.",
            ranks(72, 19, 14, start=24, count=5, cost_step=3),
            resource="health", cooldown=8, duration=3,
            target_type="enemy_aoe", max_targets=5, damage_school=SHADOW,
            source="CoA: 'Flood the minds of up to 5 nearby enemies with "
                   "visions of unraveling flesh, fearing them ... while "
                   "draining their life essence'. There is no fear mechanic "
                   "distinct from a stun, and a fear that breaks on damage "
                   "cannot coexist with its own damage, so only the drain "
                   "half ships."),
    ability("transfusion", "Transfusion", "heal",
            "Give them what they are short of. You can spare it.",
            ranks(270, 72, 44, start=34, count=4, cost_step=12),
            resource="health", cooldown=6, target_type="ally",
            source="CoA: 'Swap health percentages with an ally. Increases the "
                   "lower health percentage of the two to 40%.' A two-way "
                   "swap has no hook, so it is a one-way transfer: you pay "
                   "health, they receive it."),
    ability("blood_veil", "Blood Veil", "buff",
            "A skin of blood over an ally. It takes the first part of "
            "whatever is coming.",
            one(16, 30, 100), duration=3, target_type="ally",
            absorb_pct_max_health=0.18,
            source="CoA: 'Create a magical veil around an ally, absorbing 50% "
                   "of incoming damage'. absorb_pct_max_health is the "
                   "engine's shield field, same as Cultist's Void Shield."),
    ability("blood_rite", "Blood Rite", "revive",
            "There is enough left in them to start again. You supply the rest.",
            ranks(30, 10, 45, start=30, count=3), cooldown=20,
            target_type="ally",
            source="THE ONE INVENTED NAME IN THIS FILE. All four spec pages "
                   "state the class 'brings combat rez' in their raid rating, "
                   "and none of them names the ability; it is not in the "
                   "talent export either. Shipping the capability with a "
                   "flagged name is more faithful to the reference than "
                   "dropping a stated raid slot. effect_value is the percent "
                   "of max health revived at, as effect_type revive reads it."),

    # ---------------------------------------------------------- Sanguine
    ability("valanars_vengeance", "Valanar's Vengeance", "damage_and_heal",
            "A bolt with your own blood in it. Some of it comes back.",
            ranks(72, 19, 30, start=10, count=8, heal=40, heal_step=11),
            cooldown=2, target_type="enemy", damage_school=SHADOW,
            source="CoA: 'Valanar's Vengeance also heals you for a share of "
                   "its damage as it hits'. damage_and_heal's heal half is a "
                   "separate per-rank heal_value rather than a fraction of "
                   "the damage dealt, which is how the engine models this."),
    ability("keleseths_calamity", "Keleseth's Calamity", "spell_damage",
            "Bend the blood in a whole room at once.",
            ranks(54, 14, 35, start=20, count=6), cooldown=3,
            target_type="enemy_aoe", max_targets=4, damage_school=SHADOW,
            source="CoA: 'Bend blood in an area, dealing Shadow damage to "
                   "enemies. Each stack of Thirst reduces the cast time and "
                   "increases its damage.' The Thirst scaling has no hook; "
                   "the Rage cost is what gates it here."),
    ability("atheranns_anguish", "Atherann's Anguish", "spell_dot",
            "Plant a plague in the ground and let it work.",
            ranks(74, 20, 14, start=12, count=7, cost_step=2),
            resource="health", cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=5, damage_school=SHADOW,
            source="CoA: 'Unleash a hemoplague upon the target area, "
                   "accumulating 30% of the damage you deal to affected "
                   "enemies for 10 seconds, and then exploding for that "
                   "amount.' Bank-then-detonate has no hook, so it is a "
                   "straight ground DoT - mage_blizzard makes the same "
                   "simplification and says so."),
    ability("sanguine_rupture", "Sanguine Rupture", "spell_damage",
            "The ground opens under a pack of them and closes again.",
            ranks(42, 11, 12, start=8, count=8, cost_step=2),
            resource="health", target_type="enemy_aoe", max_targets=4,
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 22},
            source="CoA: 'Sanguine Rupture on any pack of 2+'. A health-cost "
                   "cast, so it funds the Rage it will be followed by."),
    ability("taldarams_torment", "Taldaram's Torment", "spell_dot",
            "A slow, patient wound that keeps you supplied while it works.",
            ranks(84, 22, 12, start=16, count=6, cost_step=2),
            resource="health", cooldown=4, duration=4, target_type="enemy",
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 26},
            source="CoA: Blood Parasites - 'Your Taldaram's Torment now "
                   "generates 3 additional Rage per tick'. The base ability "
                   "is a Rage-generating channel, so the generation sits on "
                   "the cast rather than per tick (status effects carry no "
                   "caster reference to grant a resource back through)."),
    ability("shadow_hemorrhage", "Shadow Hemorrhage", "spell_dot",
            "A bleed that does not clot.",
            ranks(68, 18, 12, start=4, count=8, cost_step=2),
            resource="health", duration=4, target_type="enemy",
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 16},
            source="CoA: 'Shadow Hemorrhage ticking on whatever lives "
                   "longest'. Warlock's corruption curve - a DoT's "
                   "effect_value is its per-tick potency, so the totals are "
                   "deliberately higher than a nuke's."),
    ability("malediction", "Malediction", "debuff",
            "Name what is wrong with them out loud. Everything after that "
            "lands harder.",
            one(30, 25), cooldown=5, duration=3,
            stat_mods={"magic_damage_taken_pct": 5.0}, target_type="enemy",
            buff_scope="combat",
            source="CoA: 'dealing Shadow damage over 12 seconds and "
                   "increasing the damage they take from your next 5 direct "
                   "damage spells by 20%'. The rotation wants the "
                   "damage-taken half ('Use Malediction on anything tanky for "
                   "the damage-taken debuff'), and an ability applies one "
                   "effect, so the DoT half is left to Shadow Hemorrhage. "
                   "magic_damage_taken_pct in a status effect's stat_mods is "
                   "percent POINTS - get_status_stat_mod is divided by 100 "
                   "for this key, unlike plain damage_taken_pct."),
    ability("vampiric_fang", "Vampiric Fang", "damage_and_heal",
            "Put the fang in and take it all back.",
            ranks(96, 25, 30, start=12, count=7, heal=70, heal_step=19),
            resource="vitality", target_type="enemy", damage_school=SHADOW,
            source="CoA: 'Expends Thirst Stacks. Steal health from an enemy. "
                   "Damage increased by 10% for each Thirst stack.' Thirst is "
                   "Vitality here, so this is the class's one Vitality "
                   "spender - the reference is emphatic that it 'must be used "
                   "on a timer, before Thirst caps'."),
    ability("blood_craving", "Blood Craving", "buff",
            "You want it badly enough that nothing gets between you and it.",
            one(36, 20), cooldown=14, duration=3,
            stat_mods={"cc_immune": 1, "healing_taken_pct": 30.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'for the duration you cannot be interrupted or "
                   "silenced, and you regain 5% of your maximum health and "
                   "15% of your missing Rage every 2 sec'. The health "
                   "restore lands as increased healing received, since a buff "
                   "cannot also be a heal-over-time."),
    ability("aneurysm", "Aneurysm", "debuff",
            "Something gives way behind their eyes and the sentence stops.",
            one(14, 15), cooldown=5, duration=1, target_type="enemy",
            is_stun=True, buff_scope="combat",
            source="CoA: 'Counter the enemy's spellcast, preventing any spell "
                   "from that school of magic from being cast for 4 seconds.' "
                   "There is no interrupt or school lock in this engine; a "
                   "one-turn stun is the substitution rogue_kick already "
                   "documents for Kick. The 5%-health reward for a successful "
                   "interrupt has nothing to hang on."),
    ability("sacrificial_rite", "Sacrificial Rite", "buff",
            "Spend something you will miss. Everything speeds up.",
            one(40, 30), cooldown=16, duration=3,
            stat_mods={"haste": 20.0, "healing_taken_pct": 15.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'increasing your haste by 20% for 15 seconds ... At "
                   "the end of the duration, your healing done is increased "
                   "by 15% and you are healed'. Held 'in reserve for an about "
                   "to die spike' per the rotation."),
    ability("transgression", "Transgression", "buff",
            "You stop pretending the blood is anyone else's.",
            one(44, 25), cooldown=12, duration=4,
            stat_mods={"shadow_spell_power": 30, "spell_power": 15},
            target_type="self", buff_scope="combat",
            source="CoA's Sanguine tree gates Crimson Terror and Torture off "
                   "Transgression ('grants spell damage equal to 50% of your "
                   "Spirit for the duration', 'extends the duration of "
                   "Transgression by 5 sec'), so it is a real damage window."),

    # ---------------------------------------------------------- Accursed
    ability("blood_curse", "Blood Curse", "buff",
            "Let the curse up as far as your throat and no further.",
            one(10, 20), resource="health", duration=0,
            stat_mods={"attack_power_pct": 10.0, "haste": 4.0},
            target_type="self", exclusive_group=CURSE, buff_scope="raid",
            source="CoA: the baseline Cursed Form that Accursed Form "
                   "'transforms your Blood Curse into'. Also the spec's "
                   "trickle of sustain: 'Blood Curse trickles health and Rage "
                   "the whole time you stay shifted' - no buff can trickle a "
                   "resource, so the trickle is gone and the stat half "
                   "remains. combat/forms.py defines no Bloodmage form, so "
                   "every curse is a persistent self-buff in one "
                   "exclusive_group instead of a real shapeshift."),
    ability("accursed_form", "Accursed Form", "buff",
            "Stop holding it back. What is left is faster and much worse.",
            one(20, 30), resource="health", duration=0,
            stat_mods={"attack_power_pct": 22.0, "crit_chance_physical": 4.0,
                       "armor_pct": 10.0},
            target_type="self", exclusive_group=CURSE, buff_scope="raid",
            source="CoA: 'Embrace your demonic curse ... entering an improved "
                   "Cursed Form, increasing your attack power by 50% of your "
                   "Agility'. The Agility conversion is a real engine key but "
                   "only as a talent effect, so it lives on this spec's "
                   "Forbidden Power node; the form itself carries flat "
                   "percentages. The healing-reduction debuff on its melee "
                   "has no hook."),
    ability("veinburst", "Veinburst", "spell_damage",
            "Find a vein that is already open and widen it.",
            ranks(58, 15, 12, start=6, count=8, cost_step=2),
            resource="health", cooldown=2, target_type="enemy",
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 20},
            source="CoA: 'Blast an enemy, dealing Shadow damage. Deals 25% "
                   "increased damage to bleeding targets.' The ranged half of "
                   "the spec's two modes; conditional-on-bleeding damage has "
                   "no hook, so Dark Hunt carries it as flat Shadow damage."),
    ability("hemoburst", "Hemoburst", "spell_damage",
            "Everything they have left, all at once, outward.",
            ranks(90, 24, 16, start=24, count=6, cost_step=3),
            resource="health", cooldown=4, target_type="enemy",
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 26},
            source="CoA: 'Unleash a powerful burst of blood at an enemy ... "
                   "guaranteed to critically strike against bleeding "
                   "targets.' The ranged finisher - 'Hemoburst as it closes'."),
    ability("reave", "Reave", "damage",
            "Open them up along a line you have used before.",
            ranks(60, 16, 25, start=12, count=7), cooldown=2,
            target_type="enemy", execute_threshold_pct=35,
            icon=None,
            source="CoA: 'dealing 125% Weapon Damage plus 26. the enemy is "
                   "bleeding, below 35% health, or you are behind them, deal "
                   "100% additional Shadow damage for each condition met.' "
                   "Only the below-35% condition is expressible, as "
                   "execute_threshold_pct; bleeding and positional have no "
                   "hooks. CoA strips its Rage cost in form, which the engine "
                   "cannot do conditionally, so it has a real cost."),
    ability("ravenous_strike", "Ravenous Strike", "damage_and_heal",
            "Take a bite out of the fight.",
            ranks(56, 15, 25, start=14, count=7, heal=36, heal_step=10),
            target_type="enemy", icon=None,
            source="CoA: 'Ravenous Strike healing you off the damage it deals "
                   "is a dead ringer for Death Strike', 'free and up every "
                   "GCD, and it doubles as your sustain'."),
    ability("puncturing_fangs", "Puncturing Fangs", "damage",
            "Two holes, close together, deep.",
            ranks(68, 18, 20, start=18, count=6), cooldown=3,
            target_type="enemy", icon=None,
            source="CoA lists it with Reave and Ravenous Strike as the third "
                   "transformed-melee button: 'cycle your free Reave / "
                   "Ravenous Strike / Puncturing Fangs'."),
    ability("aortic_assault", "Aortic Assault", "dot",
            "Three seconds of hitting everything within reach.",
            ranks(42, 11, 30, start=22, count=6), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=4, icon=None,
            source="CoA: 'strike nearby enemies every 1 sec for 3 seconds, "
                   "each strike causing Physical damage'. Physical, so `dot` "
                   "rather than spell_dot. The form-extension half ('Extend "
                   "the duration of your active Cursed Form by 3 sec') has no "
                   "hook, since the curses here are buffs with no timer to "
                   "extend."),
    ability("crimson_maw", "Crimson Maw", "damage",
            "Arrive teeth first.",
            ranks(52, 14, 15, start=26, count=5), cooldown=4,
            target_type="enemy", icon=None,
            source="CoA names Crimson Maw and Perilous Ascent as the spec's "
                   "mobility, in the same breath as admitting it has 'No "
                   "stun, interrupt, or silence in the spec kit'. There is no "
                   "movement in combat here, so it ships as the gap-close's "
                   "damage."),
    ability("bloodsurge", "Bloodsurge", "buff",
            "The anger arrives before you have decided anything.",
            one(30, 25), cooldown=14, duration=3,
            stat_mods={"crit_chance_spell": 10.0, "shadow_spell_power": 25,
                       "haste": 8.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'pop Bloodsurge (an enrage, Shadow damage and spell "
                   "crit up) ... for burst windows'."),
    ability("final_embrace", "Final Embrace", "buff",
            "Whatever is left of the human part goes quiet.",
            one(48, 35), cooldown=20, duration=3,
            stat_mods={"attack_power_pct": 15.0, "crit_chance_physical": 6.0,
                       "haste": 8.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'Final Embrace (a dramatically improved version of "
                   "your transformation)'. Not in the curse exclusive_group - "
                   "it is a window on top of a form, not another form."),
    ability("endure_the_curse", "Endure the Curse", "buff",
            "Being the one they are all hitting stops mattering so much.",
            one(32, 20), cooldown=14, duration=3,
            stat_mods={"damage_taken_pct": -0.3}, target_type="self",
            buff_scope="combat",
            source="CoA: 'Reduce all damage taken by -30% for 10 seconds. "
                   "While active, taking damage that would reduce your health "
                   "below 10% will instantly heal you for 30%.' The one-time "
                   "death save has no hook. 'Endure the Curse is for when you "
                   "are the one being trained.'"),

    # ----------------------------------------------------------- Eternal
    ability("eternal_curse", "Eternal Curse", "buff",
            "Stay in it. You hit softer and almost nothing gets through.",
            one(20, 30), resource="health", duration=0,
            stat_mods={"armor_pct": 25.0, "stamina_pct": 12.0,
                       "threat_generation_pct": 60, "attack_power_pct": -8.0},
            target_type="self", exclusive_group=CURSE, buff_scope="raid",
            source="CoA: 'threat, item armor and Stamina go up, damage goes "
                   "down, and the melee/tank half of the kit unlocks ... "
                   "exactly Blood/Bear presence stance math'. armor_pct, "
                   "stamina_pct and attack_power_pct are percent POINTS "
                   "(divided by 100 in _recalculate_derived_stats); "
                   "threat_generation_pct in an ability's stat_mods is also "
                   "points, the convention Guardian's Challenging Cry and "
                   "Cultist's Twilight Domain already use. The gear-only "
                   "'+200% armor from items' cannot be expressed separately "
                   "from total armour."),
    ability("ravenous_bite", "Ravenous Bite", "damage_and_heal",
            "Bite down and keep what comes loose.",
            ranks(58, 15, 25, start=12, count=7, heal=42, heal_step=12),
            target_type="enemy", icon=None,
            source="CoA: 'Ravenous Bite is a Death Strike analog, a melee "
                   "swing that heals a share of the damage it deals' - the "
                   "tank's whole sustain plan."),
    ability("bloodfang_bite", "Bloodfang Bite", "damage",
            "The workhorse bite. Nothing clever about it.",
            ranks(48, 13, 20, start=8, count=8), target_type="enemy",
            icon=None,
            source="CoA: 'Ravenous Bite and Bloodfang Bite carry both your "
                   "threat and your self-healing.' The threat filler."),
    ability("claw_sweep", "Claw Sweep", "damage",
            "One pass across the whole front rank.",
            ranks(40, 10, 25, start=16, count=6), target_type="enemy_aoe",
            max_targets=4, icon=None,
            source="CoA: 'Claw Sweep spreads threat across the pack', and "
                   "Uncanny Movement 'now generates additional threat' off "
                   "it. The pull-holding cleave."),
    ability("rotclaw", "Rotclaw", "spell_dot",
            "Leave something in the wound that should not be in a wound.",
            ranks(54, 14, 12, start=14, count=6, cost_step=2),
            resource="health", cooldown=3, duration=3,
            target_type="enemy_aoe", max_targets=4, damage_school=SHADOW,
            generates={"resource": "rage", "amount": 26},
            source="CoA: 'Ravage all nearby enemies, dealing Shadow damage, "
                   "generating Rage and infecting their wounds, causing them "
                   "to bleed.' The tank's Rage builder - 'Rotclaw keeps a "
                   "bleed and your Rage up'."),
    ability("blood_howl", "Blood Howl", "buff",
            "Every one of them decides you are the problem.",
            one(18, 20), cooldown=8, duration=2,
            stat_mods={"threat_generation_pct": 200}, target_type="self",
            buff_scope="combat",
            source="CoA: 'Blood Howl is a real AoE taunt'. Taunts are "
                   "threat_generation_pct buffs here; 200 points matches "
                   "Guardian's Challenging Cry so neither tank has a better "
                   "pull button."),
    ability("bare_fangs", "Bare Fangs", "buff",
            "Show teeth at one of them in particular.",
            one(12, 15), cooldown=4, duration=2,
            stat_mods={"threat_generation_pct": 140}, target_type="self",
            buff_scope="combat",
            source="CoA's Eternal stat priority: 'Hit/Expertise (Bare Fangs/"
                   "Blood Howl taunts ... must land)'. The single-target "
                   "taunt of that pair, so cheaper and shorter."),
    ability("night_hunters_howl", "Night Hunter's Howl", "debuff",
            "A sound that gets into their legs.",
            one(26, 25), cooldown=6, duration=2, stat_mods={"haste": -25.0},
            target_type="enemy_aoe", max_targets=5, buff_scope="combat",
            source="CoA: 'Night Hunter's Howl an AoE snare', and 'Rage comes "
                   "from landing and eating melee hits, so a disciplined "
                   "kiter throttles your whole resource engine. Night "
                   "Hunter's Howl is your only answer.' Snares are haste "
                   "debuffs here, as mage_frost_nova already does."),
    ability("eternal_resolve", "Eternal Resolve", "buff",
            "A frenzy you come out the other side of larger.",
            one(38, 30), cooldown=16, duration=3,
            stat_mods={"max_health_pct": 0.2, "haste": 12.0,
                       "healing_taken_pct": 50.0},
            target_type="self", buff_scope="combat",
            source="CoA: 'increasing your melee attack speed, maximum health, "
                   "and healing received by 50%'. All three halves exist as "
                   "real stat_mod keys; max_health_pct is the fraction one."),
    ability("monstrous_hunger", "Monstrous Hunger", "enable_instant_cast",
            "You stop waiting between bites.",
            one(34, 25), cooldown=12, duration=3, target_type="self",
            source="CoA: 'Monstrous Hunger turns your next 6 Bloodfang Bites "
                   "into halved-GCD enrage hits'. enable_instant_cast is the "
                   "engine's halved-GCD equivalent - an instant does not end "
                   "your turn. The Shadow Bats it summons need a pet template "
                   "that does not exist, so they are not here."),
    ability("hypovolemic_shock", "Hypovolemic Shock", "spell_dot",
            "They are suddenly short of the one thing they cannot borrow.",
            ranks(62, 16, 25, start=28, count=5), cooldown=5, duration=3,
            target_type="enemy", damage_school=SHADOW,
            source="CoA's Cursed Strikes extends 'the duration of Rotclaw and "
                   "Hypovolemic Shock by 50%', so Eternal has a second "
                   "bleed. Single-target, where Rotclaw is the pack one."),

    # -------------------------------------------------------- Fleshweaver
    ability("sanguine_mend", "Sanguine Mend", "heal",
            "Put them back together with what you have on hand.",
            ranks(155, 42, 30, start=6, count=8), target_type="ally",
            source="CoA: 'Sanguine Mend as your primary tank/spot heal'. The "
                   "spec's bread and butter, and the reason its Rage engine "
                   "has to keep turning."),
    ability("heartbreak", "Heartbreak", "damage_and_heal",
            "Hit one of them hard enough that your own side feels better.",
            ranks(62, 16, 35, start=14, count=7, heal=80, heal_step=22),
            cooldown=2, target_type="enemy", damage_school=SHADOW,
            heal_scope="party",
            source="CoA: 'That signature is Heartbreak, which deals Shadow "
                   "damage to a target and heals allies near it' - the "
                   "Atonement pattern the whole spec is built on. "
                   "heal_scope party is what makes the heal half land on "
                   "everyone rather than the single neediest ally."),
    ability("hemoglobe", "Hemoglobe", "hot",
            "A globe of blood over the group, giving back steadily.",
            ranks(72, 19, 16, start=30, count=5, cost_step=3),
            resource="health", cooldown=8, duration=4, target_type="party",
            generates={"resource": "rage", "amount": 30},
            source="CoA: 'healing up to 12 allies within 20 yds over 15 "
                   "seconds. Generates 2 stacks of Pooled Vitality, and 150 "
                   "Rage every 2 sec.' Pays health, heals the party over "
                   "time, and refills the Rage bar - 'drop Hemoglobe for its "
                   "pulsing AoE heal and Pooled Vitality generation'."),
    ability("crimson_tide", "Crimson Tide", "spell_dot",
            "The floor turns red under all of them at once.",
            ranks(58, 15, 35, start=22, count=6), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=5, damage_school=SHADOW,
            source="CoA: 'Create a pool of blood beneath up to 10 enemies "
                   "within 10 yds of you, causing them to bleed'. 'Crimson "
                   "Tide and Hemoglobe when the group is clustered.'"),
    ability("dark_liturgy", "Dark Liturgy", "heal",
            "A short service, said over everyone at once.",
            ranks(115, 31, 35, start=20, count=6), cooldown=3,
            target_type="party",
            source="CoA: 'healing a friendly target ... and applying Blood "
                   "Rituals to them, bouncing to up to 10 nearby allies, "
                   "healing for less for each target struck'. A bouncing heal "
                   "with falloff has no hook, so it is a flat party heal."),
    ability("darkfallen_lament", "Darkfallen Lament", "damage_and_heal",
            "Stand still and sing. It costs them and it pays you.",
            ranks(74, 20, 40, start=42, count=4, heal=130, heal_step=36),
            cooldown=10, target_type="enemy_aoe", max_targets=4,
            damage_school=SHADOW, heal_scope="party",
            source="CoA: 'healing up to 12 allies affected by Blood Rituals "
                   "... and leeching health from enemies within 10 yds. While "
                   "active, you are immune to silence and interrupt effects, "
                   "but cannot move.' The immunity and the root both need the "
                   "channel the engine does not have."),
    ability("arterial_bind", "Arterial Bind", "debuff",
            "Nobody standing in that gets a word out.",
            one(32, 30), cooldown=10, duration=2, target_type="enemy_aoe",
            max_targets=5, is_stun=True, buff_scope="combat",
            source="CoA: 'Place a pool of blood on the ground ... silencing "
                   "all enemies for 4 seconds', and the spec's only control: "
                   "'Arterial Bind's AoE silence is all you have'. No silence "
                   "category exists, so is_stun, as rogue_kick documents. The "
                   "ally-healing half of the pool is left to Hemoglobe."),
    ability("purify_blood", "Purify Blood", "dispel",
            "Draw the sickness out and leave it on the floor.",
            one(16, 15), cooldown=2, target_type="ally", dispel_type="disease",
            source="CoA: 'Purify Blood only removes a disease from an ally'. "
                   "disease is a real DispelType, so this works as written."),
    ability("hemal_excision", "Hemal Excision", "dispel",
            "Cut the curse out of an ally and hold onto it.",
            one(24, 15), cooldown=3, target_type="ally", dispel_type="curse",
            source="CoA: 'Hemal Excision only siphons curses'. The "
                   "reactivate-to-place-it-on-an-enemy half has no hook; curse "
                   "is a real DispelType, so the removal works."),
    ability("sanguine_essence", "Sanguine Essence", "buff",
            "Let the blood magic sit closer to the surface. Everything you "
            "do carries more of it.",
            one(36, 30), cooldown=12, duration=4,
            stat_mods={"healing_power_pct": 18.0, "spell_power": 25},
            target_type="self", buff_scope="combat",
            source="CoA: 'Sanguine Essence is a transformation that doesn't "
                   "lock out your caster spells. It amplifies the kit you "
                   "already have.' Deliberately NOT in the curse "
                   "exclusive_group for exactly that reason. healing_power_pct "
                   "is percent POINTS."),
    ability("gorge", "Gorge", "restore_resource",
            "Drink more than you need. You will need it.",
            one(28, 24, 0, mana_restore_pct=55), resource="health",
            cooldown=8, target_type="self", restore_resource_type="vitality",
            source="CoA: 'Instantly gain 10 stacks of Pooled Vitality every 5 "
                   "sec for 15 seconds', and 'Pop Gorge before a hard pull to "
                   "bank 10 stacks of Pooled Vitality for an empowered heal.' "
                   "Pooled Vitality is Vitality here, so this is the pool's "
                   "bulk builder."),
    ability("vampyrs_kiss", "Vampyr's Kiss", "spell_dot",
            "A small wound that makes every other wound worse.",
            ranks(76, 20, 12, start=18, count=6, cost_step=2),
            resource="health", cooldown=4, duration=4, target_type="enemy",
            damage_school=SHADOW,
            generates={"resource": "rage", "amount": 20},
            source="CoA: 'causing them to bleed ... All periodic damage dealt "
                   "to an enemy affected by Vampyr's Kiss is replicated on "
                   "them equal to 25% of the value.' The replication needs a "
                   "DoT that watches other DoTs, which does not exist; the "
                   "bleed and its Rage are real."),
    ability("infuse", "Infuse", "spell_dot",
            "Store up what you have done to them and hand it back.",
            ranks(70, 18, 30, start=34, count=4), cooldown=6, duration=3,
            target_type="enemy", damage_school=SHADOW,
            source="CoA: 'Accumulates 10% of all damage dealt to the target "
                   "and unleashes it after 10 seconds ... and absorbing "
                   "healing done to the target.' Bank-then-detonate and "
                   "healing absorption both have no hook, same as Atherann's "
                   "Anguish."),
    ability("blood_cursed_armor", "Blood-Cursed Armor", "buff",
            "A film of old blood over everyone's gear. It holds.",
            one(26, 25), duration=0, stat_mods={"armor": 160},
            target_type="self", buff_scope="raid",
            source="CoA: 'You now emanate an aura around you, increasing the "
                   "Armor of party and raid members by 390.' A pre-pull party "
                   "buff - 'put up your party buffs, Blood-Cursed Armor for "
                   "group armor'. buff_scope raid is what makes it persist "
                   "out of combat."),
    ability("bloodthorns", "Bloodthorns", "buff",
            "Thorns under an ally's skin, pointing outward.",
            one(22, 20), duration=4,
            stat_mods={"armor": 80, "physical_damage_taken_pct": -4.0},
            target_type="ally",
            source="CoA: 'Bloodthorns on whoever takes the hits'. "
                   "physical_damage_taken_pct in a status effect's stat_mods "
                   "is percent POINTS, unlike the plain damage_taken_pct "
                   "beside it, which is read raw."),
]


# ============================================================ talent helpers

def node(tree, tid, name, description, tier, slot, max_points, effects,
         *, node_type="passive", connect=None, proc=None, source=None,
         total_slots=4):
    """One talent node. `slot` is 0-based across the tier's row.

    Hex layout copies the shipped trees: hex_y = -6 + 2*tier, hex_x spaced by
    2 and centred on the row, so the tree narrows toward the capstone.
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


def debuff_proc(trigger, chance, effect_id, name, stat_mods, duration=3, icd=0):
    """A proc that lands a debuff on the TARGET.

    Status-effect stat_mods are percentage POINTS, the opposite of the talent
    effects convention, except for plain damage_taken_pct which the engine
    reads raw. Only the point-shaped keys are used below.
    """
    return {"trigger": trigger, "chance": chance, "icd": icd,
            "apply_effect": {"effect_id": effect_id, "name": name,
                             "effect_type": "debuff", "duration": duration,
                             "stat_mods": stat_mods, "on_target": True}}


# =============================================================== Sanguine
S = "bloodmage_sanguine"
SANGUINE = tree(
    S, "Bloodmage Sanguine",
    "Ranged Shadow attrition - health-cost casts bank Rage and Thirst, "
    "Thirst goes into Vampiric Fang for a lifesteal burst, and the same "
    "spells that kill the target keep you standing.",
    [
        node(S, "atheranns_wickedness", "Atherann's Wickedness",
             "Increases your Shadow damage by 2% and your hit rating by 1 per "
             "rank.",
             0, 0, 5, {"shadow_spell_damage": 0.02, "hit_rating": 1},
             source="CoA: 'Increases your Shadow damage dealt by 4% and "
                    "increases your hit chance by 3%.' <school>_spell_damage "
                    "is assembled at runtime from the school an ability "
                    "actually deals, which is why a literal grep calls it "
                    "dead."),
        node(S, "darkfallens_embrace", "Darkfallen's Embrace",
             "Increases your haste by 1 per rank.",
             0, 1, 5, {"haste": 1.0},
             source="CoA: 'Increases your spell haste by 3% and increases the "
                    "range of your Sanguine spells and Bloodbolt by 5 yds.' "
                    "There is no range stat in a turn-based engine."),
        node(S, "blood_banquet", "Blood Banquet",
             "Increases the damage of Valanar's Vengeance and Keleseth's "
             "Calamity by 4% per rank.",
             0, 2, 5, {"ability_bloodmage_valanars_vengeance_damage": 0.04,
                       "ability_bloodmage_keleseths_calamity_damage": 0.04},
             source="CoA: 'Increases the damage of Valanar's Vengeance and "
                    "Taldaram's Torment by 15%.' Pointed at the two Rage "
                    "nukes the rotation actually dumps into, since "
                    "Taldaram's Torment already has its own node."),
        node(S, "cunning_of_atherann", "Cunning of Atherann",
             "Grants spell power equal to 3% of your Stamina and 3% of your "
             "Spirit per rank.",
             0, 3, 5, {"spell_damage_from_stamina_pct": 0.03,
                       "spell_damage_from_spirit_pct": 0.03},
             source="CoA: 'Increases your spell damage by 25% of your Stamina "
                    "and Spirit.' A real <target>_from_<source>_pct "
                    "conversion, resolved against the shared STAT_CONVERSION "
                    "maps in character.py. This node is why Sanguine's stat "
                    "priority wants Spirit and Stamina on a caster."),

        node(S, "the_cup_runneth_over", "The Cup Runneth Over",
             "Increases the damage of Bloodbolt and Bloodmoon Blast by 4% per "
             "rank.",
             1, 0, 5, {"ability_bloodmage_bloodbolt_damage": 0.04,
                       "ability_bloodmage_bloodmoon_blast_damage": 0.04},
             connect=["atheranns_wickedness"],
             source="CoA: 'Increases the spell power scaling of Bloodmoon "
                    "Blast, Taldaram's Torment and Bloodbolt by 20%.' Spell "
                    "power coefficients are not per-ability here, so it is "
                    "flat damage on the two fillers."),
        node(S, "twisted_magic", "Twisted Magic",
             "Your critical strikes have a 20% chance per rank to leave the "
             "target taking 2% more magic damage from you.",
             1, 1, 3, {}, connect=["darkfallens_embrace"],
             proc=debuff_proc("on_crit", 20, "bloodmage_twisted_magic",
                              "Twisted Magic", {"magic_damage_taken_pct": 2.0}),
             source="CoA: 'Your direct harmful critical strikes increase the "
                    "target's Shadow damage taken from you by 2%, stacking up "
                    "to 5 times.' _sync_talent_procs scales a multi-rank "
                    "proc's CHANCE by points spent, not its payload, so the "
                    "ranks buy reliability rather than size. "
                    "shadow_damage_taken_pct is live at runtime but is "
                    "assembled from an f-string, so audit_talents cannot see "
                    "it and reports it dead - magic_damage_taken_pct is the "
                    "same mechanic through a key the tooling can verify."),
        node(S, "bloodwell_eruption", "Bloodwell Eruption",
             "Increases the damage your area attacks deal to additional "
             "targets by 8% per rank.",
             1, 2, 3, {"aoe_damage": 0.08}, connect=["blood_banquet"],
             source="CoA: 'Increases the radius of Sanguine Rupture by 5 yds "
                    "and its critical strike chance by 10%.' Radius is not a "
                    "thing here; the node keeps the identity by paying off "
                    "the pack hit itself."),
        node(S, "blood_parasites", "Blood Parasites",
             "Increases your spell critical strike chance by 1% per rank.",
             1, 3, 5, {"crit_chance_spell": 1.0},
             connect=["cunning_of_atherann"],
             source="CoA: 'Your Taldaram's Torment now generates 3 additional "
                    "Rage per tick and increases spell critical strike chance "
                    "against the target by 3%.' Per-target crit has no hook. "
                    "CoA's stat priority names this node as a crit payoff."),

        node(S, "lifedrinker", "Lifedrinker",
             "Increases the damage of Vampiric Fang by 6% per rank.",
             2, 0, 3, {"ability_bloodmage_vampiric_fang_damage": 0.06},
             connect=["the_cup_runneth_over"],
             source="CoA: 'Increases the damage of your Vampiric Fang by "
                    "25%.' More damage is also more lifesteal, since "
                    "damage_and_heal's heal half scales off the same node "
                    "path."),
        node(S, "enthraller", "Enthraller",
             "Increases the critical strike chance of Valanar's Vengeance and "
             "Keleseth's Calamity by 2% per rank.",
             2, 1, 5, {"ability_bloodmage_valanars_vengeance_crit": 2.0,
                       "ability_bloodmage_keleseths_calamity_crit": 2.0},
             connect=["twisted_magic"],
             source="CoA: 'Increases the critical strike chance of Valanar's "
                    "Vengeance and Keleseth's Calamity by 10%.' "
                    "ability_<id>_crit is percentage points, the same unit as "
                    "crit_chance_spell."),
        node(S, "hematoma", "Hematoma",
             "Your Bloodbolt has a 33% chance per rank to drain a share of "
             "the damage it deals back into you.",
             2, 2, 3, {}, connect=["bloodwell_eruption"],
             proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
                   "leech_pct": 0.2,
                   "ability_filter": ["bloodmage_bloodbolt"]},
             source="CoA: 'Your Bloodbolt now heals for an additional 20% of "
                    "the damage dealt.' ability_filter is what makes a proc "
                    "fire off one named ability rather than any damage cast."),
        node(S, "dominion_of_blood", "Dominion of Blood",
             "Increases the healing you do by 3% per rank.",
             2, 3, 3, {"healing_done": 0.03}, connect=["blood_parasites"],
             source="CoA: 'Your Vampiric Fang now heals you for an additional "
                    "50% of the damage dealt.' healing_done is the global "
                    "multiplier every heal and every damage_and_heal goes "
                    "through, so it covers the Fang and the rest."),

        node(S, "agonizing_pain", "Agonizing Pain",
             "Increases the damage your effects deal over time by 4% per rank.",
             3, 0, 3, {"dot_damage": 0.04}, connect=["lifedrinker"],
             source="CoA: 'Damage dealt by your Atherann's Anguish now causes "
                    "enemies hit to bleed.' A DoT spawning a second DoT has "
                    "no hook, so the node makes the ones already running "
                    "hurt more."),
        node(S, "reckless_abandon", "Reckless Abandon",
             "Increases your spell critical strike damage by 8% per rank.",
             3, 1, 2, {"crit_damage_spell": 0.08}, connect=["enthraller"],
             source="CoA: 'Each stack of Thirst now increases your critical "
                    "strike chance by 1%.' Thirst stacks are Vitality, which "
                    "nothing reads as a scaling source, so the crit identity "
                    "lands on crit damage instead."),
        node(S, "essence_harvester", "Essence Harvester",
             "While below 35% health, you take 6% less damage and are healed "
             "for 3% more, per rank.",
             3, 2, 3, {"low_health_damage_reduction_pct": 0.06,
                       "low_health_threshold_pct": 0.35,
                       "low_health_healing_pct": 0.03},
             connect=["hematoma"],
             source="CoA: 'Being struck by an enemy while below 35% health "
                    "instantly resets the cooldown of your Vampiric Fang and "
                    "grants you Wretched.' A conditional cooldown reset has "
                    "no proc shape, so the node keeps the 35% threshold and "
                    "pays off surviving there. low_health_threshold_pct is in "
                    "UNSCALED_EFFECT_KEYS, so it stays 35% at every rank."),
        node(S, "the_council_assembled", "The Council Assembled",
             "Reduces the Rage cost of Keleseth's Calamity and the health "
             "cost of Atherann's Anguish by 5% per rank.",
             3, 3, 3, {"ability_bloodmage_atheranns_anguish_cost_pct": 0.05,
                       "ability_bloodmage_keleseths_calamity_cost_pct": 0.05},
             connect=["dominion_of_blood"],
             source="CoA: 'Atherann's Anguish now costs -25 less Rage.' "
                    "POSITIVE means a reduction for a _cost_pct key - "
                    "talented_cost does cost * (1 - pct) - and eight shipped "
                    "talents once authored these negative and quietly made "
                    "their abilities more expensive."),

        node(S, "swarm_of_flies", "Swarm of Flies",
             "Increases the duration of your effects that deal damage over "
             "time by 6% per rank.",
             4, 0, 3, {"dot_duration_pct": 0.06}, connect=["agonizing_pain"],
             source="CoA: 'Your Bloodbolt now refreshes the duration of "
                    "Taldaram's Torment.' Refreshing one named DoT off "
                    "another ability has no hook; longer DoTs are the same "
                    "idea with the same payoff."),
        node(S, "dark_presence", "Dark Presence",
             "Increases your haste by 1 per rank.",
             4, 1, 3, {"haste": 1.0}, connect=["reckless_abandon"],
             source="CoA: 'Increases spell haste of all party and raid "
                    "members by 3% ... In addition, increases your spell "
                    "haste by 3%.' A talent's effects only ever modify its "
                    "owner, so only the self half is here; the party-facing "
                    "buffs in this class are abilities, where buff_scope "
                    "works."),
        node(S, "crimson_curse", "Crimson Curse",
             "Increases the damage your bleeds deal by 4% per rank.",
             4, 2, 3, {"bleed_dot_damage": 0.04},
             connect=["essence_harvester"],
             source="CoA class tree: 'Your direct damage critical strikes "
                    "increase the damage the target takes from bleed effects "
                    "by 30% for 15 seconds.' bleed_dot_damage is assembled as "
                    "f'{flavour}_dot_damage' in Ability._damage_multiplier."),

        node(S, "torture", "Torture",
             "Increases the health Vampiric Fang returns to you by 10% per "
             "rank.",
             5, 0, 2, {"ability_bloodmage_vampiric_fang_healing": 0.1},
             connect=["swarm_of_flies"], total_slots=3,
             source="CoA: 'Increases the leech of Vampiric Feast by 50%.' "
                    "ability_<id>_healing feeds the heal half of a "
                    "damage_and_heal, and was one of the suffixes that sat "
                    "dead across six classes before anything read it."),
        node(S, "thirst_for_blood", "Thirst for Blood",
             "Increases all damage you deal by 3% per rank.",
             5, 1, 2, {"all_damage": 0.03}, connect=["dark_presence"],
             total_slots=3,
             source="CoA ships this as a free level-50 passive, which Frontier "
                    "has no equivalent of, so it becomes a real node."),
        node(S, "blood_lord", "Blood Lord",
             "Increases your spell damage by 3% per rank.",
             5, 2, 2, {"spell_damage": 0.03}, connect=["crimson_curse"],
             total_slots=3,
             source="CoA: 'Grants your Bloodsore a -15% chance to provide its "
                    "benefits without being consumed.' Bloodsores are a "
                    "charge mechanic with no hook, so the node pays the spec's "
                    "main stat instead."),

        node(S, "crimson_terror", "Crimson Terror",
             "Your blood answers to you rather than the other way round. "
             "Grants spell power equal to 10% of your Spirit, and increases "
             "your Shadow damage by 5%.",
             6, 0, 1, {"spell_damage_from_spirit_pct": 0.10,
                       "shadow_spell_damage": 0.05},
             node_type="active",
             connect=["torture", "thirst_for_blood", "blood_lord"],
             total_slots=1,
             source="Capstone. CoA: 'Your Transgression now grants spell "
                    "damage equal to 50% of your Spirit for the duration.' A "
                    "window tied to one buff is not expressible as a talent, "
                    "so the conversion is permanent at a fifth of the size."),
    ],
    "Built from reference/coa_sidekick/SPEC_bloodmage__sanguine.txt: 'Closest "
    "to Affliction Warlock crossed with a Blood DK personal-survival layer. "
    "Like Affliction you pay your own health to cast, stack ramping debuffs "
    "... and grind a target down over time rather than bursting it.' The tree "
    "follows its stat priority - Spell Hit > Spell Power > Haste > Crit > "
    "Spirit/Stamina > Intellect - which is why Cunning of Atherann converts "
    "Stamina and Spirit rather than Intellect, and why Intellect appears "
    "nowhere: 'no mana pool is spent'.")


# =============================================================== Accursed
A = "bloodmage_accursed"
ACCURSED = tree(
    A, "Bloodmage Accursed",
    "Two fighting ranges in one spec - Shadow bolts from range to bank Rage, "
    "a lifestealing bruiser in Accursed Form to spend it, and no respec "
    "between them.",
    [
        node(A, "rage", "Rage",
             "Grants spell power equal to 2% of your attack power, and "
             "increases the damage of Reave by 3%, per rank.",
             0, 0, 5, {"spell_damage_from_ap_pct": 0.02,
                       "ability_bloodmage_reave_damage": 0.03},
             source="CoA: 'Increases your spell damage by 15% of your attack "
                    "power and the damage dealt by Reave by 10%.' The node "
                    "that makes a spec with a melee stat priority still hit "
                    "hard with its bolts."),
        node(A, "barely_human", "Barely Human",
             "Increases your armor penetration by 1% and the damage of "
             "Veinburst by 3%, per rank.",
             0, 1, 5, {"armor_penetration_pct": 1.0,
                       "ability_bloodmage_veinburst_damage": 0.03},
             source="CoA: 'Increases your armor penetration and the damage of "
                    "spells that cost health by 15%.' Veinburst is this "
                    "spec's main health-cost spell. armor_penetration_pct is "
                    "percentage POINTS - it is one of the ten keys "
                    "_recalculate_derived_stats divides by 100."),
        node(A, "forbidden_power", "Forbidden Power",
             "Grants spell critical strike chance equal to 4% of your Agility "
             "per rank.",
             0, 2, 5, {"crit_chance_spell_from_agility_pct": 0.04},
             source="CoA: 'Increases your spell critical strike rating by 30% "
                    "of your Agility and spell hit rating by 5% of your "
                    "Agility.' The crit half is a real conversion; hit rating "
                    "is a local feeding base_miss_chance_*, not a Character "
                    "attribute, so it cannot be a conversion target - the "
                    "same wall Guardian's Bulwark hit."),
        node(A, "killer_instinct", "Killer Instinct",
             "Increases your critical strike chance by 1% per rank.",
             0, 3, 5, {"crit_chance_physical": 1.0},
             source="CoA: 'Each point of Rage now increases the critical "
                    "strike chance of Veinburst and Reave by 0.5%.' Rage is "
                    "not a scaling source anything reads, so it is flat crit. "
                    "CoA's stat priority names this node: 'Critical Strike "
                    "(Killer Instinct/Ultra Instinct/Darkcasting are all "
                    "crit-fed)'."),

        node(A, "dark_hunt", "Dark Hunt",
             "Increases your Shadow damage by 2% per rank.",
             1, 0, 5, {"shadow_spell_damage": 0.02}, connect=["rage"],
             source="CoA: 'Increases your Shadow damage dealt by 10% against "
                    "bleeding targets.' Nothing tracks whether a target is "
                    "bleeding at damage time, so the condition is dropped and "
                    "the size cut to match."),
        node(A, "crimson_expedition", "Crimson Expedition",
             "Increases the critical strike chance of Bloodbolt and Aortic "
             "Assault by 2% per rank.",
             1, 1, 3, {"ability_bloodmage_bloodbolt_crit": 2.0,
                       "ability_bloodmage_aortic_assault_crit": 2.0},
             connect=["barely_human"],
             source="CoA: 'Increases the critical strike chance of your "
                    "Bloodbolt, Blood Shards, and Aortic Assault by 10%.' "
                    "Blood Shards are a charge mechanic with no hook."),
        node(A, "one_mans_curse", "One Man's Curse...",
             "Reduces the health cost of Accursed Form by 12% per rank.",
             1, 2, 3, {"ability_bloodmage_accursed_form_cost_pct": 0.12},
             connect=["forbidden_power"],
             source="CoA: 'Removes the health cost of Accursed Form and "
                    "entering it now instantly restores 15% of your maximum "
                    "health.' A cost reduction is expressible; the heal on "
                    "entry is not."),
        node(A, "relentless", "Relentless",
             "Increases your hit rating by 1 and your physical damage by 2% "
             "per rank.",
             1, 3, 5, {"hit_rating": 1, "physical_damage": 0.02},
             connect=["killer_instinct"],
             source="CoA ships Relentless as a free level-40 passive, which "
                    "Frontier has no equivalent of. Pointed at the spec's own "
                    "stat priority, which leads with Hit and Expertise "
                    "because 'direct-hit strikes like Reave/Ravenous "
                    "Strike/Puncturing Fangs must land'."),

        node(A, "gore_barrage", "Gore Barrage",
             "Reduces the health cost of Veinburst and Hemoburst by 6% per "
             "rank.",
             2, 0, 3, {"ability_bloodmage_veinburst_cost_pct": 0.06,
                       "ability_bloodmage_hemoburst_cost_pct": 0.06},
             connect=["dark_hunt"],
             source="CoA: 'Reduces the cost of spells that cost health and "
                    "Animated Blood by -30%.' Animated Blood is a summon with "
                    "no pet template, so only the health-cost half is here."),
        node(A, "unchained", "Unchained",
             "Increases your haste by 1 per rank.",
             2, 1, 5, {"haste": 1.0}, connect=["crimson_expedition"],
             source="CoA: 'Your damaging Mortal Form spells can now be cast "
                    "while moving.' There is no cast time and no movement in "
                    "combat here, so the free level-10 passive becomes the "
                    "nearest real benefit: acting more often."),
        node(A, "blood_shards", "Blood Shards",
             "Your damaging casts have a 20% chance per rank to carry an "
             "extra 15% damage.",
             2, 2, 3, {}, connect=["one_mans_curse"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "bonus_pct": 0.15},
             source="CoA: 'Shadow Damage dealt now generates 1 Blood Shard ... "
                    "up to 8. Dealing damage with Veinburst will now expend "
                    "all stacks of Blood Shards.' A banked-charge spender has "
                    "no hook, so it becomes a chance-based bonus on the same "
                    "hit - which is what bonus_pct is for."),
        node(A, "cruel_intent", "Cruel Intent",
             "Lunge and Crimson Maw have a 10% chance per rank to be followed "
             "by an extra weapon strike.",
             2, 3, 3, {}, connect=["relentless"],
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
                   "extra_attack": True,
                   "ability_filter": ["bloodmage_lunge",
                                      "bloodmage_crimson_maw"]},
             source="CoA: 'When you Lunge at an enemy you now strike them 3 "
                    "times with auto attacks.' extra_attack re-invokes the "
                    "caster's own bloodmage_attack for a real second swing "
                    "with its own hit and crit rolls, once - not three times, "
                    "since the payload is a flag."),

        node(A, "everlasting_hunt", "Everlasting Hunt",
             "Reduces the cooldown of Veinburst and Reave by 12% per rank.",
             3, 0, 3, {"ability_bloodmage_veinburst_cooldown_pct": 0.12,
                       "ability_bloodmage_reave_cooldown_pct": 0.12},
             connect=["gore_barrage"],
             source="CoA: 'Damage dealt by Blood Shards now reduces the "
                    "cooldown of Veinburst and Reave by -1.5 sec.' A cooldown "
                    "that always has at least one turn left (see "
                    "talented_cooldown's floor), so this cannot make either "
                    "spammable."),
        node(A, "fang_over_fang", "Fang Over Fang",
             "Increases the damage of Reave by 6% per rank.",
             3, 1, 2, {"ability_bloodmage_reave_damage": 0.06},
             connect=["unchained"],
             source="CoA: 'Casting Bloodfang Bite now has a 20% chance to "
                    "reset the cooldown of Reave.' A cooldown reset has no "
                    "proc shape, so the node buys the same thing the reset "
                    "would have: more Reave damage per fight."),
        node(A, "dark_sigil", "Dark Sigil",
             "Increases your critical strike chance with weapons and spells "
             "by 1% per rank.",
             3, 2, 3, {"crit_chance_physical": 1.0, "crit_chance_spell": 1.0},
             connect=["blood_shards"],
             source="CoA: 'Increases critical strike chance of all party and "
                    "raid members by 3% ... In addition, you now heal for 15% "
                    "of all critical damage dealt.' The party half cannot be "
                    "a talent effect; the crit half covers both of this "
                    "spec's damage types, which is the point of it."),
        node(A, "sanguine_scripture", "Sanguine Scripture",
             "Increases all damage you deal by 2% per rank.",
             3, 3, 3, {"all_damage": 0.02}, connect=["cruel_intent"],
             source="CoA: 'Upon exiting Accursed Form, you gain 70% movement "
                    "speed and spell haste for 5 seconds.' Movement speed has "
                    "no combat meaning here and the form has no exit event to "
                    "hang a buff on."),

        node(A, "battleweaver", "Battleweaver",
             "Increases your physical and spell damage by 2% per rank.",
             4, 0, 3, {"physical_damage": 0.02, "spell_damage": 0.02},
             connect=["everlasting_hunt"],
             source="CoA: 'Casting Cursed Form abilities now has a 50% chance "
                    "to generate 1 Blood Shard ... Dealing damage with "
                    "Bloodbolt will launch 1 Blood Shard.' The one node in "
                    "the tree that pays off both halves of the spec at once, "
                    "which is what it does in CoA too."),
        node(A, "crimson_feast", "Crimson Feast",
             "Reduces the cooldown of Bloodsurge by 10% per rank.",
             4, 1, 3, {"ability_bloodmage_bloodsurge_cooldown_pct": 0.1},
             connect=["fang_over_fang"],
             source="CoA: 'Every 5 second you remain in a Cursed Form now "
                    "reduces the cooldown of your Bloodsurge by -5 sec.' The "
                    "curses here are untimed buffs, so the reduction is "
                    "unconditional and smaller."),
        node(A, "terrorizer", "Terrorizer",
             "Increases the damage of Puncturing Fangs by 6% and Veinburst by "
             "4% per rank.",
             4, 2, 3, {"ability_bloodmage_puncturing_fangs_damage": 0.06,
                       "ability_bloodmage_veinburst_damage": 0.04},
             connect=["dark_sigil"],
             source="CoA: 'Increases the damage of Veinburst, Bloodfang Bite, "
                    "and Claw Sweep on enemies below 35% health by 25%.' "
                    "Bloodfang Bite and Claw Sweep belong to Eternal, so the "
                    "node points at this spec's own melee button instead, and "
                    "the health gate is dropped."),

        node(A, "night_hunter", "Night Hunter",
             "Reduces the Rage and health cost of your abilities by 3% per "
             "rank.",
             5, 0, 2, {"all_ability_cost_pct": 0.03},
             connect=["battleweaver"], total_slots=3,
             source="CoA: 'Your Veinburst now has a 40% chance to not trigger "
                    "a cooldown ... Your Bloodbolt now has a 40% chance to "
                    "refund half of its Rage cost.' A refund chance has no "
                    "hook; a flat discount is the same thing averaged out. "
                    "POSITIVE is the discount - talented_cost does cost * (1 "
                    "- pct), and Guardian, Barbarian and Felsworn all ship "
                    "this key negative, i.e. as a surcharge their tooltips "
                    "do not mention."),
        node(A, "blood_scent", "Blood Scent",
             "Your damaging casts have a 20% chance per rank to drain 12% of "
             "the damage dealt back into you.",
             5, 1, 2, {}, connect=["crimson_feast"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "leech_pct": 0.12},
             source="CoA: 'Dealing direct damage to enemies below 35% maximum "
                    "health now leeches health equal to 10% of the damage "
                    "dealt.' The execute window is not visible to a proc, so "
                    "it leeches all the time at a lower chance - and this "
                    "spec needs it, since 'Every point of sustain is "
                    "damage-gated'."),
        node(A, "darkcasting", "Darkcasting",
             "Increases your spell critical strike damage by 8% per rank.",
             5, 2, 2, {"crit_damage_spell": 0.08}, connect=["terrorizer"],
             total_slots=3,
             source="CoA lists Darkcasting with Killer Instinct and Ultra "
                    "Instinct as the spec's crit payoffs."),

        node(A, "ultra_instinct", "Ultra Instinct",
             "You stop deciding and start landing. Increases your critical "
             "strike chance by 3% and your critical strike damage by 10%, "
             "with weapons and with spells.",
             6, 0, 1, {"crit_chance_physical": 3.0, "crit_chance_spell": 3.0,
                       "crit_damage_physical": 0.1, "crit_damage_spell": 0.1},
             node_type="active",
             connect=["night_hunter", "blood_scent", "darkcasting"],
             total_slots=1,
             source="Capstone. CoA: 'Direct ability critical strikes now "
                    "increase your spell and ability critical strike chance "
                    "and critical damage by 3% for 10 sec. Each additional "
                    "critical strike increases this by an additional 3%, but "
                    "reduces its duration by -1 sec.' A self-shortening stack "
                    "has no hook, so the first stack is made permanent."),
    ],
    "Built from reference/coa_sidekick/SPEC_bloodmage__accursed.txt: 'Closest "
    "to a Feral/Guardian Druid's form-dancing bolted onto a Blood DK "
    "self-sustain layer ... No retail spec fuses ranged caster and melee "
    "lifesteal natively.' Its stat priority - Hit > Expertise > Agility > "
    "Armor Penetration > Crit > Haste - is a melee list on a spec that spends "
    "half the fight casting, which is why Rage converts attack power into "
    "spell power and Forbidden Power converts Agility into spell crit. The "
    "awkward part of the translation is that CoA strips the Rage cost off "
    "every transformed ability, and the engine has no way to make a cost "
    "conditional on a buff; Reave, Ravenous Strike and Puncturing Fangs all "
    "pay full price, and Night Hunter is the tree's apology for it.")


# ================================================================ Eternal
E = "bloodmage_eternal"
ETERNAL = tree(
    E, "Bloodmage Eternal",
    "Curse-tank - Eternal Curse trades damage for armour, Stamina and "
    "threat, Ravenous Bite heals off the damage it deals, and the whole thing "
    "stands up without a healer.",
    [
        node(E, "heightened_reflexes", "Heightened Reflexes",
             "Increases your chance to dodge by 1% and your defense rating by "
             "2 per rank.",
             0, 0, 5, {"dodge": 1.0, "defense_rating": 2},
             source="CoA: 'Increases your chance to dodge by 4% and your "
                    "expertise by 5.' Expertise is not a stat here; defense "
                    "rating is, and CoA's own stat priority leads with "
                    "'Defense (to the crit-immunity cap, non-negotiable "
                    "floor)'."),
        node(E, "eternal_hunt", "Eternal Hunt",
             "Increases your total health by 2% and reduces the cost of your "
             "abilities by 2% per rank.",
             0, 1, 5, {"max_health_pct": 0.02, "all_ability_cost_pct": 0.02},
             source="CoA: 'Increases your maximum health and reduces the cost "
                    "of your spells and abilities by 5%.' POSITIVE is the "
                    "discount on a _cost_pct key. NOTE "
                    "max_health_pct is a FRACTION - health * (1.0 + value). "
                    "Shipped at 2.0 on Guardian, it gave that tank 99,156 "
                    "effective HP against the next tank's 2,987, and "
                    "validate_class.py now fails a value an order of "
                    "magnitude off convention."),
        node(E, "uncanny_movement", "Uncanny Movement",
             "Increases your Agility by 2% and your hit rating by 1 per rank.",
             0, 2, 5, {"agility_pct": 2.0, "hit_rating": 1},
             source="CoA: 'Increases your Agility by 25% and your hit rating "
                    "by 5% of your Agility. In addition, Claw Sweep now "
                    "generates additional threat.' agility_pct is percentage "
                    "POINTS; hit rating cannot be a conversion target, so it "
                    "is flat."),
        node(E, "thick_pelt", "Thick Pelt",
             "Increases your Armor by 3% per rank.",
             0, 3, 5, {"armor_pct": 3.0},
             source="CoA: 'Physical damage taken now reduces the Physical "
                    "damage taken from the next attack within 10 seconds.' A "
                    "one-shot stacking absorb off being hit has no hook, so "
                    "the mitigation is permanent instead. 'Thick Pelt and "
                    "Shadows In The Night stack Guardian-style passive "
                    "mitigation.'"),

        node(E, "vitality", "Vitality",
             "Increases your Stamina by 2% per rank.",
             1, 0, 5, {"stamina_pct": 2.0}, connect=["heightened_reflexes"],
             source="CoA: 'Increases your Stamina while in Eternal Curse by "
                    "an additional 10%.' The engine cannot gate a talent on a "
                    "buff, so it is unconditional. CoA's priority: 'Stamina "
                    "(Eternal Curse grants +25% total Stamina ... so Stamina "
                    "is doubly amplified)'."),
        node(E, "shadows_in_the_night", "Shadows In The Night",
             "Reduces all damage you take by 2% per rank.",
             1, 1, 3, {"damage_taken_pct": -0.02}, connect=["eternal_hunt"],
             source="CoA: 'While above 75% health, your damage taken is "
                    "reduced by -5%.' There is no above-threshold conditional "
                    "to match low_health_damage_reduction_pct, so it is flat "
                    "and smaller."),
        node(E, "feral_strength", "Feral Strength",
             "Grants attack power equal to 3% of your Agility per rank.",
             1, 2, 3, {"ap_from_agility_pct": 0.03},
             connect=["uncanny_movement"],
             source="CoA: 'While in Eternal Curse, you now gain 50% more "
                    "attack power from Agility and Strength.' A real "
                    "conversion key; the form gate is dropped, as everywhere "
                    "else in this tree."),
        node(E, "no_mercy", "No Mercy",
             "Reduces the physical damage you take by 2% per rank.",
             1, 3, 5, {"physical_damage_taken_pct": -0.02},
             connect=["thick_pelt"],
             source="CoA: 'Allows your Thick Pelt to affect an additional "
                    "hit.' Thick Pelt landed as flat physical mitigation, so "
                    "the node that extends it extends the same thing."),

        node(E, "blood_moon", "Blood Moon",
             "Your damaging casts have a 33% chance per rank to drain 8% of "
             "the damage dealt back into you.",
             2, 0, 3, {}, connect=["vitality"],
             proc={"trigger": "on_damage_cast", "chance": 33, "icd": 1,
                   "leech_pct": 0.08},
             source="CoA: 'While below 75% health, you now heal for 3% of all "
                    "damage you deal.' The health gate is not visible to a "
                    "proc. 'Uncoordinated pressure cannot out-damage that.'"),
        node(E, "infection", "Infection",
             "Increases your critical strike chance by 1% per rank.",
             2, 1, 5, {"crit_chance_physical": 1.0},
             connect=["shadows_in_the_night"],
             source="CoA: 'Auto attacking a bleeding target will now infect "
                    "the wound, increasing their chance to be critically "
                    "struck from you by 1%, stacking 10 times.' A per-target "
                    "crit-taken debuff has no key, so it is the caster's own "
                    "crit - which Enraging Wounds then turns into healing."),
        node(E, "appetite_for_blood", "Appetite for Blood",
             "Increases the damage of Bloodfang Bite and Claw Sweep by 5% per "
             "rank.",
             2, 2, 3, {"ability_bloodmage_bloodfang_bite_damage": 0.05,
                       "ability_bloodmage_claw_sweep_damage": 0.05},
             connect=["feral_strength"],
             source="CoA: 'Increases the damage dealt by Bloodfang Bite and "
                    "Claw Sweep by 20% against Humanoids and Beasts.' Nothing "
                    "reads creature type in the damage path, so the condition "
                    "is dropped. These are the tank's two threat buttons, so "
                    "the node is also a threat node."),
        node(E, "rejuvenating_shadows", "Rejuvenating Shadows",
             "Increases the healing you do by 3% per rank.",
             2, 3, 3, {"healing_done": 0.03}, connect=["no_mercy"],
             source="CoA: 'Nearby party and raid members receive 6% more "
                    "healing ... In addition, increases the health leeched by "
                    "Bloodbolt by 50%.' The party aura cannot be a talent "
                    "effect and Bloodbolt has no heal half to scale, so this "
                    "is the self-healing half - which is what Ravenous Bite "
                    "and Blood Moon both run through."),

        node(E, "grim_omen", "Grim Omen",
             "Your critical strikes have a 25% chance per rank to knit you "
             "back together.",
             3, 0, 3, {}, connect=["blood_moon"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "heal_flat": 70},
             source="CoA: 'Critical strikes with Ravenous Strike or Bloodfang "
                    "Bite, or using Howl spells, now triggers Call of the "
                    "Darkwing ... healing you equal to the damage dealt.' The "
                    "Shadow Bats need a pet template that does not exist, so "
                    "the heal lands directly."),
        node(E, "iron_claws", "Iron Claws",
             "Increases your armor penetration by 1% and the damage your "
             "effects deal over time by 4% per rank.",
             3, 1, 2, {"armor_penetration_pct": 1.0, "dot_damage": 0.04},
             connect=["infection"],
             source="CoA: 'Allows Rotclaw's periodic effect to stack up 2 "
                    "additional times ... and cause you to ignore 3% of the "
                    "target's armor per stack.' Both halves exist as real "
                    "keys without the stacking that drove them."),
        node(E, "blood_mark", "Blood Mark",
             "Increases your threat generation by 6% per rank.",
             3, 2, 3, {"threat_generation_pct": 0.06},
             connect=["appetite_for_blood"],
             source="CoA: 'Increases the Physical damage taken by enemies "
                    "within 5 yds of you by 3%.' There is no aura radius "
                    "here. Note the key: threat_generation_pct as a TALENT "
                    "effect is a fraction, and all fifteen threat talents in "
                    "the game read nothing until 2026-10-28, because "
                    "combat_engine wanted threat_multiplier."),
        node(E, "dark_mark", "Dark Mark",
             "Reduces the chance you are critically hit by 1% per rank.",
             3, 3, 3, {"crit_taken_reduction": 1.0},
             connect=["rejuvenating_shadows"],
             source="CoA: 'Reduces the chance to hit for enemies within 5 yds "
                    "of you by -3%.' An aura is not expressible, and "
                    "crit_taken_reduction is the tank stat CoA's own priority "
                    "calls a 'non-negotiable floor'."),

        node(E, "uncanny_speed", "Uncanny Speed",
             "Increases your haste by 1 per rank.",
             4, 0, 3, {"haste": 1.0}, connect=["grim_omen"],
             source="CoA: 'Increases your melee haste by 5% and your movement "
                    "speed and mounted movement speed by 20%.' Only the haste "
                    "half means anything in combat."),
        node(E, "rabid", "Rabid",
             "Reduces the cooldown of Blood Howl and Night Hunter's Howl by "
             "10% per rank.",
             4, 1, 3, {"ability_bloodmage_blood_howl_cooldown_pct": 0.1,
                       "ability_bloodmage_night_hunters_howl_cooldown_pct": 0.1},
             connect=["iron_claws"],
             source="CoA: 'Reduces the cooldown of Howl spells by -25%.' Both "
                    "Howls this spec actually presses, by name."),
        node(E, "eternal_presence", "Eternal Presence",
             "Increases your attack power by 3% per rank.",
             4, 2, 3, {"attack_power_pct": 3.0}, connect=["blood_mark"],
             source="CoA: 'Increases the attack power of party and raid "
                    "members by 5% ... In addition, you now gain attack power "
                    "equal to 15% of the damage taken for 10 seconds.' "
                    "Neither the aura nor the damage-taken scaling is "
                    "expressible; attack power is threat for this spec, which "
                    "is why it is here at all. attack_power_pct is percentage "
                    "POINTS."),

        node(E, "bloodmoon_power", "Bloodmoon Power",
             "Grants dodge equal to 3% of your Agility, and increases the "
             "damage your effects deal over time by 4%, per rank.",
             5, 0, 2, {"dodge_from_agility_pct": 0.03, "dot_damage": 0.04},
             connect=["uncanny_speed"], total_slots=3,
             source="CoA: 'Periodic damage dealt by Rotclaw now hits -50% "
                    "more often and your Bloodfang Bite, Claw Sweep, and "
                    "Bloodbolt additionally scales with dodge rating.' The "
                    "engine converts stats INTO dodge, not dodge into damage, "
                    "so the direction is reversed and the DoT half kept."),
        node(E, "enraging_wounds", "Enraging Wounds",
             "Your critical strikes have a 40% chance per rank to leech 20% "
             "of the damage dealt.",
             5, 1, 2, {}, connect=["rabid"], total_slots=3,
             proc={"trigger": "on_crit", "chance": 40, "icd": 0,
                   "leech_pct": 0.2},
             source="CoA: 'Melee critical strikes now leech health from the "
                    "target, scaling with your Stamina.' Scaling a proc off a "
                    "stat has no hook, so it scales off the hit instead - "
                    "which is the same direction, since Stamina is what makes "
                    "the hits survivable."),
        node(E, "bloody_claws", "Bloody Claws",
             "Increases your physical damage by 3% per rank.",
             5, 2, 2, {"physical_damage": 0.03}, connect=["eternal_presence"],
             total_slots=3,
             source="CoA: 'You now generate 20% increased Rage from damage "
                    "dealt and critical strikes with auto attacks now reduces "
                    "the cooldown of Animated Blood, Blood Veil, and Blood "
                    "Pact by 1 sec.' Rage generation here is an ability's "
                    "`generates` block, which a talent cannot scale except "
                    "through a proc's scale_talent_key; the damage half is "
                    "what remains."),

        node(E, "eyes_in_the_night", "Eyes In The Night",
             "Nothing gets behind you. You take 12% less damage, hold 10% "
             "more threat, and carry 6% more health.",
             6, 0, 1, {"damage_taken_pct": -0.12, "threat_generation_pct": 0.1,
                       "max_health_pct": 0.06},
             node_type="active",
             connect=["bloodmoon_power", "enraging_wounds", "bloody_claws"],
             total_slots=1,
             source="Capstone. CoA: 'Allies within 20 yds are protected by "
                    "Shadow Colony, giving them a 40% chance to trigger a "
                    "Call of the Darkwing when they take direct damage ... "
                    "generate a large amount of threat against the enemy that "
                    "triggered it.' The ally-facing half needs both a pet "
                    "template and a party-wide talent effect, neither of "
                    "which exists, so the threat and the survival stay with "
                    "the tank."),
    ],
    "Built from reference/coa_sidekick/SPEC_bloodmage__eternal.txt: 'Closest "
    "to a Guardian Druid / Blood Death Knight hybrid ... No single retail spec "
    "does both the deep-mitigation tanking and the vampiric self-heal at "
    "once.' CoA rates it Dungeon S, which is the gap the tank roster keeps "
    "running into. Its stat priority is Defense > Stamina > Hit/Expertise > "
    "Armor > Agility > Crit/Haste, so the tree spends its early rows on "
    "defense rating, Stamina and Armor and only buys crit where crit turns "
    "into healing (Infection into Enraging Wounds). The repeated compromise "
    "in this tree is that almost every CoA node is gated on holding Eternal "
    "Curse, and nothing can gate a talent on a buff, so the gates are dropped "
    "and the magnitudes cut to pay for it.")


# ============================================================ Fleshweaver
F = "bloodmage_fleshweaver"
FLESHWEAVER = tree(
    F, "Bloodmage Fleshweaver",
    "Blood-paid support - pay health to bank Rage, spend Rage on shields and "
    "instant heals, and damage the pack with the same casts that top the "
    "group up.",
    [
        node(F, "gift_of_lanathel", "Gift of Lana'thel",
             "Grants spell power equal to 3% of your Spirit, and 1 hit "
             "rating, per rank.",
             0, 0, 5, {"spell_power_from_spirit_pct": 0.03, "hit_rating": 1},
             source="CoA: 'increasing your spell power by 25% of your Spirit "
                    "and your hit rating by 4% of your Spirit.' The spell "
                    "power half is a real conversion; hit rating cannot be a "
                    "conversion target, so it is flat. This node is why the "
                    "spec's stat priority reads Spell Power > Spirit."),
        node(F, "organ_orbs", "Organ Orbs",
             "Increases your Spirit by 2% per rank.",
             0, 1, 5, {"spirit_pct": 2.0},
             source="CoA: 'Each stack of Pooled Vitality now increases your "
                    "Spirit by 3%.' Vitality is not a scaling source anything "
                    "reads, so the Spirit is unconditional. spirit_pct is "
                    "percentage POINTS."),
        node(F, "consolidation", "Consolidation",
             "Increases your haste by 1 per rank.",
             0, 2, 5, {"haste": 1.0},
             source="CoA: 'Increases your haste by 5%.' CoA's priority puts "
                    "Haste above Crit for 'more frequent Hemoglobe pulses/"
                    "Crimson Tide windows in a dot-transmute healing style'."),
        node(F, "raging_hunger", "Raging Hunger",
             "Your damaging casts have a 20% chance per rank to return 4 Rage.",
             0, 3, 5, {}, proc={"trigger": "on_damage_cast", "chance": 20,
                                "icd": 1,
                                "grant_resource": {"resource": "rage",
                                                   "amount": 4}},
             source="CoA: 'Triggering Pooled Vitality now also generates 3 "
                    "Rage.' The spec's named weakness is its cold start - "
                    "'an ambush at 0 Rage leaves you no shield and no panic "
                    "button' - and this is the node that answers it. "
                    "grant_resource goes through the same gain_resource() "
                    "every builder ability uses, so the 100 cap holds."),

        node(F, "teachings_of_lanathel", "Teachings of Lana'thel",
             "Grants spell critical strike chance equal to 3% of your Spirit "
             "per rank.",
             1, 0, 5, {"crit_chance_spell_from_spirit_pct": 0.03},
             connect=["gift_of_lanathel"],
             source="CoA's stat priority names it: 'Teachings of Lana'thel "
                    "converts Spirit straight into spell hit and spell crit "
                    "rating'. Crit is a real conversion target; spell hit is "
                    "not."),
        node(F, "excess_blood", "Excess Blood",
             "Increases the healing you do by 3% per rank.",
             1, 1, 3, {"healing_done": 0.03}, connect=["organ_orbs"],
             source="CoA: 'Your healing done now has a 10% chance to heal the "
                    "target for an additional amount over 6 seconds.' A heal "
                    "that spawns a HoT has no hook; flat healing is the same "
                    "throughput without the second effect."),
        node(F, "spice_of_life", "Spice of Life",
             "Increases the damage your effects deal over time by 4% per rank.",
             1, 2, 3, {"dot_damage": 0.04}, connect=["consolidation"],
             source="CoA: 'Your periodic damage and healing now has a 10% "
                    "chance to grant a stack of Pooled Vitality.' Periodic "
                    "effects carry no caster reference to grant a resource "
                    "back through, so the node pays off the periodic damage "
                    "itself - which is how Crimson Tide and Vampyr's Kiss "
                    "earn their place in a healing rotation."),
        node(F, "blood_redistribution", "Blood Redistribution",
             "Increases the healing done by Fleshcraft by 5% per rank.",
             1, 3, 5, {"ability_bloodmage_fleshcraft_healing": 0.05},
             connect=["raging_hunger"],
             source="CoA: 'Increases the maximum health restored by "
                    "Fleshcraft by 25%.' Fleshcraft is the spec's "
                    "'Pain Suppression/Guardian Spirit-tier stop-the-bleeding "
                    "button', so it gets a dedicated node."),

        node(F, "black_heart", "Black Heart",
             "Your heals have a 25% chance per rank to return 6 Rage.",
             2, 0, 3, {}, connect=["teachings_of_lanathel"],
             proc={"trigger": "on_heal_cast", "chance": 25, "icd": 1,
                   "grant_resource": {"resource": "rage", "amount": 6}},
             source="CoA: 'Your Vampyr's Rage now regenerates 20% of your "
                    "maximum Rage', and 'Vampyr's Kiss refunding Rage behind "
                    "them'. The second half of a Rage economy that otherwise "
                    "only fills by spending health."),
        node(F, "sanguine_scion", "Sanguine Scion",
             "Increases the critical strike chance of Sanguine Mend and "
             "Bloodbolt by 2% per rank.",
             2, 1, 5, {"ability_bloodmage_sanguine_mend_crit": 2.0,
                       "ability_bloodmage_bloodbolt_crit": 2.0},
             connect=["excess_blood"],
             source="CoA: 'Increases the critical strike chance of Sanguine "
                    "Mend and Bloodbolt by 10%.' Both named abilities exist "
                    "here, so this is the one node that needed no "
                    "translation."),
        node(F, "waves_of_blood", "Waves of Blood",
             "Your heals have a 33% chance per rank to spill 20% of their "
             "value onto your other allies.",
             2, 2, 3, {}, connect=["spice_of_life"],
             proc={"trigger": "on_heal_cast", "chance": 33, "icd": 0,
                   "splash_heal": 0.2},
             source="CoA: 'Each tick of Crimson Tide now has a 10% chance to "
                    "heal a nearby ally for 25% of the damage dealt.' A DoT "
                    "tick cannot heal anyone, so the splash moves onto the "
                    "spec's heals, where splash_heal is the engine's existing "
                    "spread-to-other-allies payload."),
        node(F, "universal_donor", "Universal Donor",
             "Increases your healing power by 2% per rank.",
             2, 3, 3, {"healing_power_pct": 2.0},
             connect=["blood_redistribution"],
             source="CoA: 'Casting Infuse or Vampyr's Kiss now increases the "
                    "healing received by all allies by 6%.' healing_taken_pct "
                    "is only ever read off a status effect, never off a "
                    "talent, so a talent authored on it would look right and "
                    "do nothing - this grants healing power instead, which is "
                    "the same outcome from the other end."),

        node(F, "gruesome_rituals", "Gruesome Rituals",
             "Increases all damage you deal by 2% per rank.",
             3, 0, 3, {"all_damage": 0.02}, connect=["black_heart"],
             source="CoA: 'Your damage dealt is now increased by 1% for each "
                    "stack of Pooled Vitality.' Vitality is not readable as a "
                    "scaling source, so the bonus is flat."),
        node(F, "dissipation", "Dissipation",
             "Reduces the cooldown of Fleshcraft by 12% per rank.",
             3, 1, 2, {"ability_bloodmage_fleshcraft_cooldown_pct": 0.12},
             connect=["sanguine_scion"],
             source="CoA: 'Reduces the cooldown of Fleshcraft and the "
                    "duration of the Sated debuff by -60 sec.' Sated has no "
                    "hook; the cooldown is what actually gates Fleshcraft "
                    "here."),
        node(F, "crimson_scion", "Crimson Scion",
             "Reduces the Rage cost of your heals by 2% per rank.",
             3, 2, 3, {"heal_cost_pct": 0.02}, connect=["waves_of_blood"],
             source="CoA: 'Direct damage dealt now has a 10% chance to make "
                    "your next Sanguine Mend within 10 seconds instant cast.' "
                    "Everything here is already instant, so the node pays the "
                    "other currency a free cast saves. POSITIVE is a "
                    "reduction for a _cost_pct key."),
        node(F, "vitality_for_later", "Vitality For Later",
             "Grants healing power equal to 3% of your Spirit per rank.",
             3, 3, 3, {"healing_power_from_spirit_pct": 0.03},
             connect=["universal_donor"],
             source="CoA: 'Consuming Pooled Vitality now heals up to 10 "
                    "allies within 30 yds, scaling with Spirit and healing "
                    "power.' A consumption trigger has no hook; the Spirit "
                    "scaling is a real conversion and is the half worth "
                    "keeping."),

        node(F, "sovereignty", "Sovereignty",
             "Increases the damage your area attacks deal to additional "
             "targets by 8% per rank.",
             4, 0, 3, {"aoe_damage": 0.08}, connect=["gruesome_rituals"],
             source="CoA: 'Damage dealt by Crimson Tide now grants you "
                    "Sovereignty ... causes it to strike 1 additional nearby "
                    "enemy for each target damaged.' Target count is fixed per "
                    "ability by max_targets, so the node makes the extra "
                    "targets hurt more instead."),
        node(F, "heart_rupturer", "Heart Rupturer",
             "Increases the damage of Heartbreak and Crimson Tide by 5% per "
             "rank.",
             4, 1, 3, {"ability_bloodmage_heartbreak_damage": 0.05,
                       "ability_bloodmage_crimson_tide_damage": 0.05},
             connect=["dissipation"],
             source="CoA: 'Increases the damage of Claw Sweep, Sanguine "
                    "Rupture, Ravenous Strike and Bloodmoon Blast by 20%.' "
                    "Three of those four belong to other specs, so the node "
                    "points at the two abilities this rotation actually "
                    "presses - and Heartbreak's damage is also its healing."),
        node(F, "invigorated_flesh", "Invigorated Flesh",
             "Increases your hit rating by 1 and your spell critical strike "
             "chance by 1% per rank.",
             4, 2, 3, {"hit_rating": 1, "crit_chance_spell": 1.0},
             connect=["crimson_scion"],
             source="CoA ships this as a free level-20 passive granting the "
                    "whole raid 1% hit, which Frontier has no equivalent of "
                    "and a talent cannot grant party-wide, so it becomes a "
                    "real node for its owner."),

        node(F, "fleshbending", "Fleshbending",
             "Increases your spell critical strike chance by 2% per rank.",
             5, 0, 2, {"crit_chance_spell": 2.0}, connect=["sovereignty"],
             total_slots=3,
             source="CoA: 'Your critical strikes now increase the critical "
                    "strike chance of all party and raid members by 5%.' The "
                    "party half cannot be a talent effect."),
        node(F, "red_thirst", "Red Thirst",
             "Increases your haste by 2 per rank.",
             5, 1, 2, {"haste": 2.0}, connect=["heart_rupturer"],
             total_slots=3,
             source="CoA: 'Enrage allies within 40 yds, increasing haste by "
                    "30% for 20 seconds.' A raid haste cooldown is an "
                    "ability, not a talent effect; the self half is what fits "
                    "here."),
        node(F, "bloodcraft", "Bloodcraft",
             "Increases your spell damage by 3% per rank.",
             5, 2, 2, {"spell_damage": 0.03}, connect=["invigorated_flesh"],
             total_slots=3,
             source="CoA: 'Your damage dealt by Darkfallen Lament now applies "
                    "Bloodcraft to affected enemies, reducing damage dealt by "
                    "-2%.' An enemy damage-dealt debuff has no key in the "
                    "engine's stat vocabulary."),

        node(F, "flesh_foundry", "Flesh Foundry",
             "You stop running out of material. Grants critical strike chance "
             "equal to 6% of your Spirit, increases your healing by 8%, and "
             "cuts Fleshcraft's cooldown by 20%.",
             6, 0, 1, {"crit_chance_from_spirit_pct": 0.06,
                       "healing_done": 0.08,
                       "ability_bloodmage_fleshcraft_cooldown_pct": 0.2},
             node_type="active",
             connect=["fleshbending", "red_thirst", "bloodcraft"],
             total_slots=1,
             source="Capstone. CoA: 'Your critical strikes now reduce the "
                    "cooldown of Fleshcraft and the duration of Sated on the "
                    "target by -4 sec. In addition, increases your critical "
                    "strike rating by 15% of your Spirit.' A crit-driven "
                    "cooldown reduction has no hook, so the reduction is "
                    "unconditional and the Spirit conversion is real."),
    ],
    "Built from reference/coa_sidekick/SPEC_bloodmage__fleshweaver.txt: "
    "'Closest to Discipline Priest, with a dash of Blood DK bolted on ... No "
    "single retail healer runs an Atonement-style AoE loop off a "
    "Rage-from-health-cost economy like this.' Its stat priority is Spell "
    "Power > Spirit > Stamina > Haste > Crit > Intellect, with Intellect last "
    "because 'no mana is ever spent' - which is why three nodes in this tree "
    "convert Spirit and none touch Intellect. Two nodes exist purely to keep "
    "the Rage engine turning (Raging Hunger, Black Heart), because the spec's "
    "own stated weakness is a cold start at zero Rage and this class has no "
    "passive Rage regeneration at all.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Bloodmage",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/bloodmage.json", ability_doc),
        (ROOT / "data/talents/bloodmage_sanguine.json", SANGUINE),
        (ROOT / "data/talents/bloodmage_accursed.json", ACCURSED),
        (ROOT / "data/talents/bloodmage_eternal.json", ETERNAL),
        (ROOT / "data/talents/bloodmage_fleshweaver.json", FLESHWEAVER),
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
