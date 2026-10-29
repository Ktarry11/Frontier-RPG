#!/usr/bin/env python3
"""Author the Reaper: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_reaper.py [--apply]

SOURCE. reference/coa_sidekick/CLASS_reaper.txt, the three
SPEC_reaper__*.txt pages and reference/coa_sidekick/talents/reaper.json,
captured from ascensionsidekick.com. Every ability and talent name below is
a real CoA name off those pages; nothing is invented to fill a slot. CoA's
blurb: "warriors who have come upon a dark and hungry spirit trapped inside
a scythe, born of souls the Lich King imprisoned within enchanted Hungering
Scythes." Identity per that reference:

  Harvest     MELEE DPS  "Closest to Blood Death Knight." The Harvester
                         passive turns a share of ALL damage dealt into
                         healing, so the loop is hit things and stay full.
                         Executes under 35% with Slaughter.
  Soul        MELEE DPS  "Closest to retail Vengeance Demon Hunter" wearing
                         "a rogue-flavored stealth-and-mobility duelist
                         chassis". Generators cascade into Soul Harvest;
                         Shadowfrost magic does as much work as the weapon.
  Domination  TANK       Also Vengeance, but the attrition half: overlapping
                         mitigation layers that deepen the longer the fight
                         runs, plus real party support (Ethereal Guard,
                         Soulsight, Spectral Warden).

RESOURCE. CLASS_RESOURCE_MAP gives Reaper (MANA, SOULS) - Mana is the
primary pool and Souls the 0-100 secondary (Character.
SECONDARY_RESOURCE_MAX, no override), which is how CoA's single Runic Power
bar plus its Soul Fragment / Reaped Soul / Soul Infusion stack economy lands
in an engine with exactly two pools. Mana gates the rotation, so Mana costs
SCALE WITH RANK the way Cultist's do (same Mana-primary-plus-builder shape);
Souls costs are FLAT, because a 0-100 pool that refills from generators does
not care what level you are. Builders carry a `generates` block, spenders set
resource_type "souls".

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference is a fan-made planning tool
whose own disclaimer says COA is pre-meta. Damage curves copy Warrior's and
Guardian's shipped LINEAR shape (base + step per rank, 9 ranks at levels
1/6/12/18/24/32/40/48/56) because Reaper is another Strength-flavoured mail
melee class and should scale alongside them. Mana costs copy Cultist's
geometric ramp, scaled down: Reaper's level-60 pool is 780 against Cultist's
1050, so a filler sits near 6% of the bar and the heaviest strike near 12%.

SCHOOL SPLIT, stated once because it is the one thing a Reaper player has to
know. effect_type "damage" resolves through the PHYSICAL multiplier path
(Ability._damage_multiplier(caster, "physical")) no matter what
damage_school says, while "spell_damage"/"spell_dot"/"damage_and_heal" go
through the SPELL path and pick up <school>_spell_damage talents. So every
weapon strike here is left untagged and scales off physical_damage/
all_damage, and everything the reference calls Shadow or Shadowfrost is
authored as real spell damage with damage_school set. Authoring a weapon
strike as "Shadowfrost damage" would have produced a tooltip whose school
talents silently did nothing - the same failure mode
data/abilities/cultist.json records on Entropic Strike.

Talent effect keys are restricted to ones the engine actually reads -
verified with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. Casualties worth recording:

  souls_max   get_resource_max() really does read f"{key}_max" for any
              secondary pool, so a souls_max talent WOULD work at runtime.
              But "souls_max" appears as a literal nowhere in the engine and
              is not in audit_talents._NAMED_LIVE (which lists static_max,
              energy_max, insanity_max, runes_max, solar_power_max by hand),
              so the validator calls it dead. No node uses it; Soul Tap and
              Sinister Litany carry the resource-economy slack instead.
  healing_taken_pct
              read only through get_status_stat_mod, never
              get_talent_effect, so it works on a BUFF and is dead on a
              TALENT. Domination's Soul Knight is a flat magic-damage
              reduction instead of the healing-received half.
  "more damage against enemies below X% health"
              Hemorrhage, The Jailer's Call and Final Requiem all key off
              the TARGET's health, which _damage_multiplier has no
              recipient for. Each lands on the execute ability itself
              (Slaughter) rather than as a conditional multiplier.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Warrior's and Guardian's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]

#: Per-rank Mana cost growth. 1.14 over 8 steps is 2.85x, against a Mana
#: pool that grows 2.53x from level 1 to 56, so an ability gets slowly more
#: expensive as a share of the bar - the same mild creep Cultist's kit has
#: (Blade of the Empire goes 5.9% -> 19.7% of its pool across its ranks).
MANA_COST_GROWTH = 1.14


def _levels(start, count):
    """Rank levels, on the shipped schedule when the ability starts at 1.

    Later abilities are spaced evenly to stay at or below 58 so every rank
    is actually reachable at the level 60 cap.
    """
    if start == 1:
        return RANK_LEVELS[:count]
    span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
    return [min(58, start + i * span) for i in range(count)]


def ranks(base, step, cost, *, start=1, count=9, flat_cost=False,
          heal=0, heal_step=0, restore=0):
    """Rank table. Mana costs ramp; Souls costs are flat (see docstring).

    `heal` fills the separate heal_value rank key that damage_and_heal
    reads - effect_value alone leaves the heal at zero, which is how
    guardian_final_verdict shipped a self-heal that heals nothing.
    `restore` fills mana_restore_pct, which restore_resource reads for the
    same reason.
    """
    out = []
    for i, level in enumerate(_levels(start, count)):
        rank = {
            "rank": i + 1,
            "level_req": level,
            "cost": cost if flat_cost else int(round(cost * MANA_COST_GROWTH ** i)),
            "effect_value": int(round(base + step * i)),
        }
        if heal:
            rank["heal_value"] = int(round(heal + heal_step * i))
        if restore:
            rank["mana_restore_pct"] = restore
        out.append(rank)
    return out


def one(level, cost, value=0, *, restore=0, heal=0):
    """Single-rank table, for cooldowns and stances that do not scale."""
    rank = {"rank": 1, "level_req": level, "cost": cost, "effect_value": value}
    if heal:
        rank["heal_value"] = heal
    if restore:
        rank["mana_restore_pct"] = restore
    return [rank]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None,
            resource="mana", **extra):
    out = {
        "ability_id": f"reaper_{aid}",
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


def souls(amount):
    """A `generates` block for the Souls pool."""
    return {"resource": "souls", "amount": amount}


# ============================================================== ability kit
# Order is roughly the order a player meets them: shared chassis first, then
# the three specs' own buttons.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured swing of the scythe.", one(1, 0, 0),
            source="Convention: every class ships a free rank-1 Attack. Also "
                   "the ability the engine re-invokes for an extra_attack "
                   "proc, found by the <class>_attack naming rule."),

    # ---- shared chassis: the generators and spenders all three specs press
    ability("reap", "Reap", "damage",
            "A short, economical cut that leaves a soul loose in the air for "
            "you to take.",
            ranks(36, 9, 16), target_type="enemy", generates=souls(10),
            source="CoA: Reap is the builder in all three rotations - "
                   "Domination's 'keep Reap flowing', Harvest's 'Reap as "
                   "your basic filler', Soul's 'fill gaps with Reap, the "
                   "cheap generator'. Class tree's Backswing raises the "
                   "resource it returns, so it generates Souls as well as "
                   "costing Mana. Warrior's heroic_strike curve."),
    ability("murder", "Murder", "damage",
            "Two fast strikes to the same spot, which is usually enough.",
            ranks(50, 13, 26, start=6, count=8), cooldown=2,
            target_type="enemy", generates=souls(15),
            source="CoA: 'Murder on cooldown while closing, or on a second "
                   "target, for free extra Soul Fragments'. The class tree's "
                   "Mysterious Omen extends its range, so it is class kit "
                   "rather than any one spec's."),
    ability("soul_strike", "Soul Strike", "damage_and_heal",
            "Reach past the body for what is underneath it, and take some "
            "back with you.",
            ranks(84, 22, 30, start=10, count=7, heal=40, heal_step=11),
            cooldown=2, target_type="enemy", heal_scope=1,
            damage_school="shadow", icon=None,
            source="CoA: Domination's 'Soul Strike as your Runic Power "
                   "spender and health/Strength steal (Essence Binder)', and "
                   "the class tree's Harvester's Scythe 'increases the amount "
                   "leeched by Soul Strike'. damage_and_heal is the engine's "
                   "only life-steal effect_type; note it resolves on the "
                   "SPELL damage path, which is why this is Shadow-schooled "
                   "and carries a high flat base rather than reading as a "
                   "weapon hit."),
    ability("wraithblade", "Wraithblade", "damage",
            "A blow the scythe lands somewhere other than here, so there is "
            "nothing in the way of it.",
            ranks(96, 26, 46, start=14, count=6), cooldown=4,
            target_type="enemy", generates=souls(25),
            source="CoA class tree: 'Generates 3 Reaped Souls. Strike for "
                   "150% Weapon Damage plus AP Shadow damage, ignoring "
                   "resistances, absorption, and invulnerability effects.' "
                   "Soul calls it 'your hardest hitting opener'. The "
                   "ignore-everything clause has no engine hook - there is no "
                   "way to bypass resistance or an absorb shield on a single "
                   "cast - so it is a plain big physical hit with the "
                   "largest Souls grant in the kit."),
    ability("soulrend", "Soulrend", "spell_dot",
            "The wound will not close while the scythe still remembers it.",
            ranks(30, 8, 24, start=8, count=6), cooldown=3, duration=3,
            target_type="enemy", damage_school="shadow", icon=None,
            source="CoA: Soul's Weakened Souls and Haunter both modify "
                   "Soulrend, Domination's Soulstorm refunds souls off it, "
                   "and Harvest's Callous Soul makes it ignore armour - all "
                   "three specs' trees touch it, so it is class kit."),
    ability("scythe_rush", "Scythe Rush", "damage",
            "Cover the ground between you in two strides and open with the "
            "hook of the blade.",
            ranks(50, 16, 20, start=12, count=5), cooldown=5,
            target_type="enemy", generates=souls(15),
            source="CoA class tree: 'Rush towards an enemy and generate 15 "
                   "Runic Power. Cannot be used on the same target more than "
                   "once every 20 seconds.' The per-target lockout has no "
                   "engine hook; a 5 turn cooldown stands in for it."),
    ability("spectre_stride", "Spectre Stride", "damage",
            "You arrive before the sound of you does.",
            ranks(64, 20, 28, start=22, count=5), cooldown=4,
            target_type="enemy", generates=souls(10),
            source="CoA: the class tree's Ghastly Advance extends it and "
                   "Between Shadows makes it generate a Reaped Soul; Soul's "
                   "Apparition raises its damage 30%. Soul lists it under "
                   "'Spectre Stride closes'."),
    ability("soul_harvest", "Soul Harvest", "damage_and_heal",
            "Spend what you have taken. It goes back into you as fast as it "
            "comes out of them.",
            ranks(72, 20, 30, start=16, count=6, flat_cost=True,
                  heal=72, heal_step=20),
            cooldown=1, resource="souls", target_type="enemy", heal_scope=1,
            damage_school="shadow", icon=None,
            source="CoA class tree: 'Soul Harvest (Damage): Blasts your "
                   "target for Shadow Damage, healing for 100% of the damage "
                   "dealt.' In CoA it is a free cascade off generating Reaped "
                   "Souls; here it is the Souls SPENDER, because a 0-100 pool "
                   "needs somewhere to go and this is the class's signature "
                   "effect. Heal equals damage, as the tooltip says."),
    ability("soul_shear", "Soul Shear", "spell_damage",
            "A clean cut through something that was never physical.",
            ranks(86, 24, 34, start=24, count=5), cooldown=3,
            target_type="enemy", damage_school="shadow", icon=None,
            source="CoA: named in the class tree's Into The Shadow Realm and "
                   "Soul's Reaver, both of which cut its cooldown alongside "
                   "Deathstalker and Soulstone Lure. The reference never "
                   "states its damage, so it is sized as the mid-cooldown "
                   "Shadow nuke those two nodes imply."),
    ability("ghastly_screech", "Ghastly Screech", "spell_dot",
            "A sound that gets into the throat and stays there, and then "
            "gets worse.",
            ranks(36, 11, 38, start=34, count=4), cooldown=6, duration=2,
            target_type="enemy_aoe", max_targets=4,
            damage_school=["shadow", "frost"], icon=None,
            source="CoA class tree: 'Screech with ghastly intent, silencing "
                   "all nearby enemies for 4 seconds, and dealing AP "
                   "Shadowfrost Damage at the end of the duration.' There is "
                   "no silence primitive, so the damage-at-the-end half "
                   "carries the ability as a short AoE Shadowfrost dot."),
    ability("deathwind", "Deathwind", "hot",
            "Stand in it. Whatever is leaving you, some of it comes back.",
            ranks(120, 36, 32, start=26, count=4), cooldown=8, duration=3,
            target_type="self", icon=None,
            source="CoA: Domination's 'Deathwind for sustain on a tough "
                   "single target or when you've overpulled', and Harvest's "
                   "Hungering Scythe extends it, so both specs want it. The "
                   "real ability is a ground zone; this engine has no "
                   "positional areas, so it is a self heal-over-time."),
    ability("veilwalk", "Veilwalk", "buff",
            "Step half out of the world. Things move slower on the other "
            "side of it.",
            one(16, 20), cooldown=6, duration=2,
            stat_mods={"haste": 10.0, "dodge": 5.0}, target_type="self",
            icon=None,
            source="CoA class tree: '2 Charges. 50% increased movement speed "
                   "for 5 seconds, stacking 2 times. Removes all movement "
                   "impairing effects.' Movement speed is not modelled in a "
                   "turn engine and 'movement' is NOT a real DispelType (see "
                   "DispelType.ALL), so authoring this as a dispel would have "
                   "made a button that always fails and refunds. Haste and "
                   "dodge are the honest turn-based reading of moving faster "
                   "than the thing swinging at you."),
    ability("soul_tap", "Soul Tap", "restore_resource",
            "Take the edge off your own soul. It grows back, mostly.",
            one(18, 25, 25, restore=25), cooldown=4, resource="souls",
            target_type="self", restore_resource_type="mana", icon=None,
            source="CoA class tree: 'Chip away at the very essence of your "
                   "own soul, generating 50 Runic Power.' With Mana as the "
                   "primary pool this is the Souls-into-Mana valve, the same "
                   "shape as cultist_sanity_tap. mana_restore_pct is on the "
                   "rank because that, not effect_value, is the key "
                   "restore_resource actually reads."),
    ability("sinister_litany", "Sinister Litany", "restore_resource",
            "Say the quiet part out loud and three of them answer.",
            one(20, 24, 35, restore=35), cooldown=6, target_type="self",
            restore_resource_type="souls", icon=None,
            source="CoA class tree: 'Embrace your sinister thoughts, "
                   "instantly generating 3 Reaped Souls.' 35% of a 100 pool "
                   "stands in for 3 of a 5-stack bank."),
    ability("ghost_claw", "Ghost Claw", "debuff",
            "Something cold closes on the back of their leg.",
            one(22, 22), cooldown=4, duration=2,
            stat_mods={"haste": -20.0}, target_type="enemy", icon=None,
            source="CoA: 'Ghost Claw (Speed): Chill an enemy with a ghostly "
                   "claw, slowing and stealing -50% of their movement speed "
                   "for 8 seconds.' Movement speed becomes attack speed, the "
                   "only slow a turn engine can express."),
    ability("tormented_souls", "Tormented Souls", "buff",
            "Keep one of them awake and screaming where it can take the hits "
            "meant for you.",
            one(24, 35), cooldown=8, duration=3, resource="souls",
            stat_mods={"damage_taken_pct": -0.10}, target_type="self",
            icon=None,
            source="CoA class tree: 'Tormented Souls: Reduces all direct "
                   "damage you take by 10% and heals you for Stamina, "
                   "removing 1 stack.' The stack-consuming heal has no hook; "
                   "the 10% mitigation is literal. NOTE damage_taken_pct in a "
                   "buff's stat_mods is read RAW by take_damage, so -0.10 is "
                   "-10% - the OPPOSITE convention to the school-specific "
                   "variants beside it, which are divided by 100."),
    ability("jailers_bargain", "Jailer's Bargain", "buff",
            "Ask him for something and he always says yes. That is the "
            "problem with him.",
            one(26, 30), cooldown=10, duration=3, target_type="self",
            absorb_pct_max_health=0.30, icon=None,
            source="CoA class tree: 'gaining a shield that absorbs damage "
                   "equal to 30% of your maximum health for 10 seconds. "
                   "While this is active you are considered Undead and are "
                   "immune to fear, sleep, and charm effects.' The absorb is "
                   "literal; there is no creature-type swap or "
                   "immunity-to-a-school-of-CC primitive."),
    ability("withering_touch", "Withering Touch", "debuff",
            "Lay a hand on their armour and it ages a hundred years under "
            "your palm.",
            one(28, 26), cooldown=5, duration=3,
            stat_mods={"armor": -140, "magic_damage_taken_pct": 10.0},
            target_type="enemy", generates=souls(10), icon=None,
            source="CoA class tree: 'reducing the target's armor by -20% and "
                   "increasing their Magic damage taken by 10% for 1 minute, "
                   "and generates Runic Power.' Armour reduction is flat "
                   "rather than proportional because a debuff's stat_mods are "
                   "a flat bonus pool. magic_damage_taken_pct on a DEBUFF is "
                   "percentage POINTS (take_damage divides it by 100), hence "
                   "10.0 and not 0.10."),
    ability("limbo", "Limbo", "buff",
            "Step out of your own body for a moment. Nothing aimed at it "
            "lands.",
            one(30, 36), cooldown=15, duration=2,
            stat_mods={"magic_damage_taken_pct": -45.0,
                       "damage_taken_pct": -0.15},
            target_type="self", icon=None,
            source="CoA class tree: 'Rip out of your mortal shell for 5 "
                   "seconds, making you immune to all harmful spell effects "
                   "and instantly restoring 30% of your maximum health and "
                   "Runic Power.' All three specs name it as the answer to "
                   "magic burst. There is no immunity primitive and no way to "
                   "pair a heal with a buff on one cast, so it is a heavy "
                   "magic-damage reduction plus a smaller flat one; the "
                   "health-and-resource restore is gone and Jailer's Bargain "
                   "carries the shield half of the class's defensive kit."),
    ability("shadows_embrace", "Shadow's Embrace", "dispel",
            "Whatever got into their head, you take it out again.",
            one(32, 24), cooldown=6, target_type="ally",
            dispel_type="magic", icon=None,
            source="CoA: Domination's 'Shadow's Embrace cleanses fear, charm "
                   "and sleep one effect at a time'. Fear, charm and sleep "
                   "are Magic in WoW's dispel schools, and magic is a real "
                   "DispelType here, so this one survives translation intact."),
    ability("masochistic_rage", "Masochistic Rage", "buff",
            "Open your own skin first. After that nothing they do is news.",
            one(36, 30), cooldown=10, duration=3,
            stat_mods={"damage_dealt_pct": 20.0}, target_type="self",
            icon=None,
            source="CoA class tree: 'After a 1 sec delay, you suffer AP "
                   "damage, enraging you and increasing your damage dealt by "
                   "20% for 15 seconds.' The self-damage cost has no hook, so "
                   "a long cooldown pays for it instead. damage_dealt_pct in "
                   "a buff is percentage POINTS."),
    ability("soulstone_lure", "Soulstone Lure", "debuff",
            "Show them a way out that was never there.",
            one(38, 32), cooldown=10, duration=2, target_type="enemy",
            is_stun=True, icon=None,
            source="CoA: Domination's 'hard CC stops at Mark of Terror's "
                   "fear and Soulstone Lure's horrify'. A horrify is a stun "
                   "here; is_stun is the only incapacitate the engine has."),

    # ---- Harvest
    ability("crows_harvest", "Crow's Harvest", "damage",
            "A full turn with the scythe out, and every one of them loses "
            "something.",
            ranks(36, 10, 30, start=10, count=7), cooldown=3,
            target_type="enemy_aoe", max_targets=4, generates=souls(20),
            source="CoA: 'Open with Crow's Harvest to leap into the pull, "
                   "deal weapon damage in an arc, and harvest up to 3 Soul "
                   "Fragments.' max_targets=4 rather than target_type alone, "
                   "because enemy_aoe on its own hits EVERY enemy in the "
                   "fight - the limited-cleave cap is what the tooltip means."),
    ability("doomrend", "Doomrend", "damage",
            "Open them from the collarbone down and leave the wound arguing "
            "with anything that tries to close it.",
            ranks(78, 21, 34, start=16, count=6), cooldown=4,
            target_type="enemy", generates=souls(15),
            source="CoA: 'Doomrend to apply its anti-heal shield and, with "
                   "Darkrend Scythe, start the bleed.' An ability's own "
                   "`proc` is only attached for buff/debuff effect_types, so "
                   "a damage ability cannot apply its own debuff: the "
                   "anti-heal lives on the Blood Fueled talent instead, where "
                   "a proc CAN land a healing_taken_pct debuff on the target."),
    ability("slaughter", "Slaughter", "damage",
            "They are already finished. This is bookkeeping.",
            ranks(120, 34, 36, start=20, count=6), cooldown=2,
            target_type="enemy", execute_threshold_pct=35,
            generates=souls(20),
            source="CoA: 'Slaughter the moment a target drops below 35% HP "
                   "for the execute plus a Reaped Soul.' execute_threshold_pct "
                   "is 0-100, not a fraction - guardian_final_verdict shipped "
                   "0.25 and gated itself at a quarter of one percent."),
    ability("sever", "Sever", "damage_and_heal",
            "Cut the thread the words are travelling down.",
            ranks(96, 28, 34, start=30, count=4, heal=60, heal_step=18),
            cooldown=5, target_type="enemy", heal_scope=1,
            damage_school="shadow", icon=None,
            source="CoA: 'Attempt to drain an enemies vitals, leeching AP "
                   "health, interrupting casting and preventing any spell "
                   "from that school from being cast for 3 seconds.' There is "
                   "no interrupt or school-lockout primitive, so the leech "
                   "half is the whole ability and 'Sever to interrupt a "
                   "dangerous cast' is lost."),
    ability("harvesting_grounds", "Harvesting Grounds", "debuff",
            "Mark the ground. Leaving it turns out to be harder than they "
            "expected.",
            one(28, 30), cooldown=8, duration=3,
            stat_mods={"haste": -15.0}, target_type="enemy_aoe",
            max_targets=5, icon=None,
            source="CoA: 'enemies inside have their melee and ranged haste "
                   "and movement speed reduced by -20%. For the duration, "
                   "enemies that try to exit the harvesting ground will be "
                   "pulled back to its center.' The haste slow is literal; "
                   "the zone and the pull-back are not modellable."),
    ability("harvest_time", "Harvest Time", "buff",
            "Decide the fight is over and then spend a while proving it.",
            one(40, 34), cooldown=12, duration=3,
            stat_mods={"damage_dealt_pct": 15.0,
                       "crit_chance_physical": 15.0},
            target_type="self", requires_talent=True, icon=None,
            source="CoA: 'Increases your damage and critical strike chance by "
                   "15% ... for 15 seconds', 'your burst window when you can "
                   "commit to a heavy trade'. Taught by the Harvest Time "
                   "talent; the Soul-Infusion-preservation clause has no "
                   "equivalent with a single Souls pool."),
    ability("blood_frenzy", "Blood Frenzy", "spell_dot",
            "It stops being a fight and becomes weather.",
            ranks(90, 30, 44, start=48, count=2), cooldown=10, duration=3,
            target_type="enemy", damage_school="shadow",
            requires_talent=True, icon=None,
            source="CoA: 'Deals AP Shadow Damage to your target every 0.75 "
                   "sec for 7.5 seconds. At the end of the duration, the "
                   "target takes an additional AP Shadow Damage.' The "
                   "end-of-duration spike has no hook, so it is a plain heavy "
                   "Shadow dot. Capstone-taught, like CoA's tier gate."),

    # ---- Soul
    ability("dirge", "Dirge", "damage",
            "The same two notes, over and over, until something gives.",
            ranks(58, 15, 30, start=12, count=7), cooldown=2,
            target_type="enemy", generates=souls(20),
            source="CoA: 'Loop Dirge (dual-weapon strike, generates 2 Soul "
                   "Fragments) as your main sustained button.' Reaper is "
                   "two-hand only in Frontier (weapon_types.json: sword_2h, "
                   "axe_2h, mace_2h), so the dual-wield framing is dropped "
                   "and it reads as a repeated two-handed strike. Its "
                   "Shadowfrost school is dropped too - see the SCHOOL SPLIT "
                   "note; a 'damage' ability never reads school talents."),
    ability("deathchaser", "Deathchaser", "spell_dot",
            "Name them once. It keeps going back on its own after that.",
            ranks(34, 10, 28, start=14, count=6), cooldown=4, duration=3,
            target_type="enemy", damage_school=["shadow", "frost"],
            generates=souls(10), icon=None,
            source="CoA: 'Open with Deathchaser (repeating Shadowfrost "
                   "damage, generates Runic Power, reapplies on sub-20% "
                   "targets) to soften and mark the target.' Real Shadowfrost "
                   "- authored as a combined-school list, which "
                   "get_resistance resolves to the LOWEST component "
                   "resistance. Chasing Death's sub-20% reapplication has no "
                   "hook."),
    ability("reliquary_of_the_lost", "Reliquary of the Lost", "spell_damage",
            "Open the box. Everything in it goes the same direction.",
            ranks(130, 36, 35, start=20, count=6, flat_cost=True),
            cooldown=3, resource="souls", target_type="enemy",
            damage_school="shadow", icon=None,
            source="CoA: 'Whenever Soul Infusion comes up, fire Reliquary of "
                   "the Lost (Purgatory has ramped its damage)'. The spec's "
                   "biggest single-target spender; Soul Infusion's gate "
                   "becomes the Souls cost."),
    ability("soulslam", "Soulslam", "damage",
            "Put everything you are carrying into the ground at once.",
            ranks(54, 16, 40, start=26, count=5, flat_cost=True),
            cooldown=4, resource="souls", target_type="enemy_aoe",
            max_targets=5,
            source="CoA: 'dump Reaped Souls into Soulslam if 2+ mobs are "
                   "clustered', 'That is your best AoE damage'. The other "
                   "Souls spender, and the reason the pool is worth banking "
                   "on a trash pull."),
    ability("ghostly_weapon", "Ghostly Weapon", "buff",
            "The blade goes cold enough that the air around it complains.",
            one(18, 24), cooldown=8, duration=4,
            stat_mods={"damage_dealt_pct": 12.0}, target_type="self",
            icon=None,
            source="CoA: 'Imbue your weapon with ghostly power for 15 "
                   "seconds, causing melee attacks to deal 25% additional "
                   "damage as Frost damage.' An imbue that re-schools your "
                   "autoattacks is not expressible, so it is a flat "
                   "damage-dealt window; Lamenting's heal off that Frost "
                   "damage is folded into the Soul tree as a leech proc."),
    ability("shade", "Shade", "buff",
            "Become the part of the room nobody looks at.",
            one(32, 28), cooldown=15, duration=2,
            stat_mods={"dodge": 25.0, "damage_taken_pct": -0.20},
            target_type="self", icon=None,
            source="CoA: 'Become a shade, entering an improved stealth mode "
                   "for 10 seconds and entering Underwalk. Removes all "
                   "movement impairing effects.' No stealth in combat, so "
                   "'nothing can find you' lands as heavy avoidance plus flat "
                   "mitigation - the second of the spec's two defensive outs."),
    ability("deaths_presence", "Death's Presence", "buff",
            "Standing near you is bad for them and good for everyone else.",
            one(24, 30), target_type="self", buff_scope="raid",
            stat_mods={"damage_dealt_pct": 3.0}, requires_talent=True,
            icon=None,
            source="CoA: 'Increases all damage dealt by party and raid "
                   "members by 3%. Does not stack with similar effects.' The "
                   "spec's whole party toolkit, which the reference lists as "
                   "a weakness: 'A partner under pressure gets no heal, no "
                   "shield and no CC-break from you.'"),
    ability("endbringer", "Endbringer", "buff",
            "For a little while you are the last thing that happens here.",
            one(44, 40), cooldown=18, duration=3,
            stat_mods={"damage_dealt_pct": 20.0, "haste": 10.0},
            target_type="self", requires_talent=True, icon=None,
            source="CoA: 'Become an Endbringer for 15 seconds, increasing the "
                   "damage of Dirge by 30%, the range by 20 yds, and causes "
                   "it to generate 3 Reaped Souls. For the duration, Dirge "
                   "will heal you for 75% of its damage dealt.' A buff cannot "
                   "reach inside one named ability, so it is a general burst "
                   "window; Gravesite's crit damage rides on the same talent."),
    ability("sepulchral_renewal", "Sepulchral Renewal", "reset_cooldowns",
            "You have been dead before. It did not take.",
            one(48, 44), cooldown=20, target_type="self", icon=None,
            source="CoA: 'Resets the cooldown of Limbo, Soulslam, and Shade.' "
                   "The reference calls this the answer to the spec's named "
                   "weakness - 'Limbo and Shade are finite cooldowns. Spend "
                   "both and there is a dead window.' reset_cooldowns is "
                   "whole-book here rather than a named list."),

    # ---- Domination
    ability("dreadwake", "Dreadwake", "damage",
            "A wave of them goes out ahead of the blade and arrives first.",
            ranks(40, 11, 30, start=12, count=7), cooldown=2,
            target_type="enemy_aoe", max_targets=3, generates=souls(15),
            source="CoA: 'Dreadwake (cone, Weapon plus Frost damage, "
                   "generates a Reaped Soul) as your main filler once you're "
                   "on a 2H weapon'. A 12 yd cone becomes a 3-target cleave."),
    ability("requiem", "Requiem", "damage",
            "Everything within reach of the swing hears the same thing.",
            ranks(34, 10, 34, start=18, count=6), cooldown=4,
            target_type="enemy_aoe", max_targets=5, generates=souls(10),
            source="CoA: 'Swing at enemies around you in a fury of souls, "
                   "dealing AP Shadowfrost Damage, reducing their melee and "
                   "ranged attack speed by 20% for 15 seconds.' One cast "
                   "cannot both damage and debuff, so the attack-speed slow "
                   "moves to the Soulstorm talent as a proc and this keeps "
                   "the AoE damage and threat the tank rotation needs."),
    ability("decimate", "Decimate", "damage",
            "Every sixth cut lands somewhere the first five were only asking "
            "about.",
            ranks(100, 26, 40, start=28, count=5), cooldown=3,
            target_type="enemy",
            source="CoA: Decimation, Domination's level-50 passive - 'Reap, "
                   "whose every 6th cast turns into a Decimate'. A cast "
                   "counter has no hook, so Decimate is its own "
                   "short-cooldown heavy strike rather than a Reap "
                   "replacement."),
    ability("bolstered_form", "Bolstered Form", "buff",
            "Set yourself. The souls in the haft take the next few for you.",
            one(16, 0), cooldown=10, duration=3,
            stat_mods={"armor_pct": 25.0, "parry": 10.0},
            target_type="self", generates={"resource": "mana", "amount": 60},
            icon=None,
            source="CoA: 'Assume a bolstered form for 15 seconds, generating "
                   "30 Runic Power, increasing your Armor by 25%, and "
                   "increasing your parry chance by 25%.' Costs nothing and "
                   "GENERATES, exactly as written. Parry trimmed from 25 to "
                   "10 points because nothing else in the game hands out a "
                   "quarter of an avoidance table. armor_pct in stat_mods is "
                   "percentage POINTS, which is why it is 25.0."),
    ability("spectral_scythe", "Spectral Scythe", "summon_pet",
            "Let one of them loose on its own recognisance.",
            one(34, 35), cooldown=6, resource="souls", target_type="self",
            summon_pet_template="spectral_scythe", icon=None,
            source="CoA: 'Summons 1 Spectral Scythe for each Reaped Soul "
                   "active which attack a nearby enemy for 20 seconds. "
                   "Striking enemies with Soul Strike causes the Spectral "
                   "Scythe to attack that enemy and 5 nearby enemies. "
                   "Consumes Reaped Souls and Soul Infusion'. Souls-costed, "
                   "as written. NOW A REAL SPECTRAL SCYTHE: this used to "
                   "borrow faceless_destroyer, the Cultist's pet, on the "
                   "reasoning that there was no spectral-blade template and "
                   "pet_templates.py was shared. There is one now - a "
                   "floating animated weapon rather than a body, lowest "
                   "health and highest crit chance of any pet in the game. "
                   "Still one body per cast, not one per banked soul "
                   "(Character.EXTRA_PET_CAP has no Reaper entry), and the "
                   "5-target Soul Strike cleave is still not expressible on "
                   "a pet."),
    ability("spectral_warden", "Spectral Warden", "summon_pet",
            "Something large and patient stands up between you and them.",
            one(44, 44), cooldown=15, target_type="self",
            summon_pet_template="spectral_warden", requires_talent=True,
            icon=None,
            source="CoA: 'Summon a spectral guardian to fight along side you "
                   "for 20 seconds and apply an absorption shield to up to 8 "
                   "allies within 20 yds, absorbing Stamina damage.' NOW A "
                   "REAL SPECTRAL WARDEN: this used to borrow voidwalker and "
                   "summoned a pet named Voidwalker - the engine's existing "
                   "tank-shaped shadow pet, which was the right shape and a "
                   "Warlock demon. The template now exists, built as the "
                   "durable counterpart to this class's own Spectral Scythe "
                   "(more health and armour, deliberately less damage). "
                   "summon_pet still cannot also shield the party and the "
                   "group absorb is still lost - the template's _source "
                   "records why a pet-cast absorb buff would be dead data "
                   "rather than a fix. Taught by the Spirit Army talent."),
    ability("ethereal_guard", "Ethereal Guard", "buff",
            "Your presence takes the edge off whatever is coming for the "
            "rest of them.",
            one(30, 32), target_type="self", buff_scope="raid",
            stat_mods={"damage_taken_pct": -0.03}, requires_talent=True,
            icon=None,
            source="CoA: 'Reduces the damage taken by party and raid members "
                   "by -3%. Does not stack with similar effects. In addition, "
                   "increases your melee haste by 10%.' One buff cannot aim "
                   "two different stat sets at two different sets of targets, "
                   "so the party mitigation is kept and the personal haste "
                   "moves into the Hard Bargain talent."),
    ability("eater_of_souls", "Eater of Souls", "buff",
            "Three of them at once is enough to live on for a while.",
            one(40, 40), cooldown=10, duration=3, resource="souls",
            stat_mods={"physical_damage_taken_pct": -10.0},
            target_type="self", icon=None, requires_talent=True,
            proc={"trigger": "on_damage_taken", "chance": 100, "icd": 0,
                  "heal_flat": 70},
            source="CoA: 'Reaching 3 Reaped Souls now reduces your Physical "
                   "damage taken by -10% and you regain 1% of your maximum "
                   "health every 2 sec for 10 seconds.' A resource THRESHOLD "
                   "trigger has no hook, so it is a Souls-costed cooldown "
                   "instead - you still have to bank three souls' worth to "
                   "press it. The regen half is the on-damage-taken heal "
                   "proc, since the buff is only up while being hit anyway. "
                   "physical_damage_taken_pct on a buff is POINTS."),
    ability("soulsight", "Soulsight", "buff",
            "You show them where the seams are.",
            one(38, 30), target_type="self", buff_scope="raid",
            stat_mods={"crit_chance_physical": 3.0, "crit_chance_spell": 3.0},
            icon=None,
            source="CoA: 'Increases critical strike chance of all party and "
                   "raid members by 3%. Does not stack with similar effects.' "
                   "The second half of what the reference calls 'Rare support "
                   "from a tank'."),
    ability("mark_of_terror", "Mark of Terror", "debuff",
            "Put the mark on one of them and the ones beside it notice.",
            one(36, 34), cooldown=12, duration=2, target_type="enemy_aoe",
            max_targets=3, is_stun=True, icon=None,
            source="CoA: Domination's 'hard CC stops at Mark of Terror's fear "
                   "and Soulstone Lure's horrify'. A fear is is_stun here; "
                   "capped at 3 targets so it is a peel and not a full-pull "
                   "lockdown."),
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


def dot_proc(trigger, chance, effect_id, name, potency, duration, *,
             school="shadow", abilities=None, icd=0):
    """A proc that opens a damage-over-time wound on the target.

    `abilities` becomes ability_filter, the engine's real per-ability proc
    gate (combat/status_effects.py) - without it an on_damage_cast proc
    fires off ANY cast, which is how a talent that says "your Doomrend"
    quietly becomes "everything you do".
    """
    proc = {"trigger": trigger, "chance": chance, "icd": icd,
            "apply_effect": {
                "effect_id": effect_id,
                "name": name,
                "effect_type": "dot",
                "duration": duration,
                "potency": potency,
                "damage_school": school,
                "on_target": True}}
    if abilities:
        proc["ability_filter"] = [f"reaper_{a}" for a in abilities]
    return proc


def soul_proc(trigger, chance, amount, *, abilities=None, icd=0):
    """A proc that harvests Souls."""
    proc = {"trigger": trigger, "chance": chance, "icd": icd,
            "grant_resource": {"resource": "souls", "amount": amount}}
    if abilities:
        proc["ability_filter"] = [f"reaper_{a}" for a in abilities]
    return proc


# =============================================================== Harvest
H = "reaper_harvest"
HARVEST = tree(
    H, "Reaper Harvest",
    "Lifesteal brawler - the Harvester passive turns a share of everything "
    "you deal into healing, Doomrend stops the target stabilising, and "
    "Slaughter finishes anything under 35%.",
    [
        node(H, "bountiful_harvest", "Bountiful Harvest",
             "Increases the damage of Reap and Murder by 5% per rank.",
             0, 0, 5, {"ability_reaper_reap_damage": 0.05,
                       "ability_reaper_murder_damage": 0.05},
             source="CoA: 'Increases the damage of Reap and Murder by 25%'. "
                    "Split across 5 ranks to reach the same total."),
        node(H, "sanguine_harvester", "Sanguine Harvester",
             "Increases your haste by 1 per rank.",
             0, 1, 5, {"haste": 1.0},
             source="CoA: 'Increases your melee haste by 10%', 2 ranks. "
                    "Frontier's haste is a flat rating, and 1.0/rank is the "
                    "shipped per-rank value across every tree."),
        node(H, "crimson_wraith", "Crimson Wraith",
             "Increases your critical strike damage by 4% per rank.",
             0, 2, 5, {"crit_damage_physical": 0.04},
             source="CoA: 'Increases your critical stike damage by 10%'. "
                    "crit_damage_physical is a FRACTION of the base hit."),
        node(H, "callous_soul", "Callous Soul",
             "Increases your armor penetration by 2% per rank.",
             0, 3, 5, {"armor_penetration_pct": 2.0},
             source="CoA: 'Increases the amount of armor Soulrend causes you "
                    "to ignore by 10%'. There is no per-ability armour-ignore "
                    "key, so it is general armour penetration - which the "
                    "spec's stat priority asks for anyway ('Strength > Armor "
                    "Penetration > Critical Strike'). armor_penetration_pct "
                    "is one of the ten POINTS keys, hence 2.0 for 2%."),

        node(H, "red_wake", "Red Wake",
             "Your critical strikes have a 20% chance per rank to harvest a "
             "Soul.",
             1, 0, 3, {}, connect=["bountiful_harvest"],
             proc=soul_proc("on_crit", 20, 10),
             source="CoA: 'Direct damage critical strikes now generate an "
                    "additional Soul Fragment.' A multi-rank proc scales its "
                    "CHANCE by points spent (_sync_talent_procs) and not its "
                    "payload, so the tooltip says chance per rank."),
        node(H, "maw_knight", "Maw Knight",
             "Increases the critical strike chance of Doomrend by 4% per "
             "rank.",
             1, 1, 5, {"ability_reaper_doomrend_crit": 4.0},
             connect=["sanguine_harvester"],
             source="CoA: 'Increases the critical strike chance of Doomrend "
                    "by 5%'. ability_<id>_crit is in percentage POINTS - it "
                    "is added straight onto crit_chance."),
        node(H, "doomer", "Doomer",
             "Increases the damage of Doomrend and Slaughter by 6% per rank.",
             1, 2, 5, {"ability_reaper_doomrend_damage": 0.06,
                       "ability_reaper_slaughter_damage": 0.06},
             connect=["crimson_wraith"],
             source="CoA: 'Increases the damage of Doomrend and Slaughter by "
                    "30%'. Five ranks of 6% is the same 30%."),
        node(H, "dark_fate", "Dark Fate",
             "Reduces the Mana cost of Crow's Harvest by 6% per rank.",
             1, 3, 3, {"ability_reaper_crows_harvest_cost_pct": 0.06},
             connect=["callous_soul"],
             source="CoA: 'Reduces the cost of Crow's Harvest by -10 Runic "
                    "Power.' POSITIVE means a reduction on a _cost_pct key - "
                    "eight talents across four classes authored these "
                    "negative and delivered a surcharge."),

        node(H, "harvester", "Harvester",
             "Your damage heals you for 15% of the damage dealt.",
             2, 0, 1, {}, connect=["red_wake"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                   "leech_pct": {"pct": 0.15}},
             source="CoA's level-10 free passive and the whole reason to play "
                    "the spec: 'You now heal yourself equal to 15% of all "
                    "damage dealt', 'pure lifesteal that trivializes "
                    "downtime'. Frontier has no free passives, so it is a "
                    "single-point node early in the tree. One point, not "
                    "five, because a proc's PAYLOAD does not scale with rank "
                    "and a 5-rank version would read as 75% and deliver 15%."),
        node(H, "blood_fueled", "Blood Fueled",
             "Your Doomrend has a 34% chance per rank to leave the target "
             "receiving 30% less healing for 3 turns.",
             2, 1, 3, {}, connect=["maw_knight"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["reaper_doomrend"],
                   "apply_effect": {
                       "effect_id": "reaper_doomrend_antiheal",
                       "name": "Doomrend",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"healing_taken_pct": -30.0},
                       "on_target": True}},
             source="CoA: 'Increases the healing absorbed by Doomrend by 30%', "
                    "on top of Doomrend's own 'dark shield to them that "
                    "absorbs the next healing done to them'. Doomrend itself "
                    "cannot carry a proc (only buff/debuff abilities do), so "
                    "the anti-heal lives here, gated to Doomrend with "
                    "ability_filter. healing_taken_pct is read only through "
                    "get_status_stat_mod, which is exactly why it has to be a "
                    "proc's stat_mod and could not be a plain effect."),
        node(H, "genocide", "Genocide",
             "Increases the critical strike chance of Slaughter by 4% and its "
             "critical damage by 5% per rank.",
             2, 2, 3, {"ability_reaper_slaughter_crit": 4.0,
                       "ability_reaper_slaughter_crit_damage": 0.05},
             connect=["doomer"],
             source="CoA: 'Increases the critical damage and critical strike "
                    "chance of Slaughter by 10%.'"),
        node(H, "crimson_thirst", "Crimson Thirst",
             "Your strikes have a 15% chance per rank to build Crimson "
             "Thirst, increasing your damage by 4% for 3 turns.",
             2, 3, 5, {}, connect=["dark_fate"],
             proc={"trigger": "on_damage_cast", "chance": 15, "icd": 0,
                   "apply_effect": {
                       "effect_id": "reaper_crimson_thirst",
                       "name": "Crimson Thirst",
                       "effect_type": "buff",
                       "duration": 3,
                       "max_stacks": 5,
                       "stat_mods": {"damage_dealt_pct": 4.0},
                       "on_target": False}},
             source="CoA: 'Your Physical damage dealt now grants Crimson "
                    "Thirst for 20 seconds, stacking 5 times ... Your next "
                    "Murder deals 10% increased damage and costs -10% less "
                    "per stack. At 5 stacks, it also heals you equal to 50% "
                    "of the damage dealt.' max_stacks=5 is real here - a "
                    "stacking effect's stat_mods are PER STACK. The "
                    "Murder-only targeting and the 5-stack heal are dropped; "
                    "Harvester already carries the spec's leech."),

        node(H, "souls_for_the_slaughter", "Souls for the Slaughter",
             "Your critical strikes have a 25% chance per rank to leave "
             "Shadow rot on the target for 2 turns.",
             3, 0, 3, {}, connect=["harvester"],
             proc=dot_proc("on_crit", 25, "reaper_souls_for_the_slaughter",
                           "Souls for the Slaughter", 70, 2),
             source="CoA: 'Critical strikes with Slaughter now cause your "
                    "auto attacks to deal an additional 85% Shadow damage for "
                    "5 seconds.' Added Shadow damage on autoattacks has no "
                    "hook, so the Shadow goes onto the target as a dot "
                    "instead. Not filtered to Slaughter: Slaughter only fires "
                    "under 35% health, and a proc that can only roll during "
                    "an execute window is a dead talent in practice."),
        node(H, "hungering_scythe", "Hungering Scythe",
             "Increases the damage of Crow's Harvest by 6% per rank, and your "
             "Deathwind lasts 1 turn longer.",
             3, 1, 2, {"ability_reaper_crows_harvest_damage": 0.06,
                       "ability_reaper_deathwind_duration": 1},
             connect=["blood_fueled"],
             source="CoA: 'Increases the duration of Deathwind by 4 sec and "
                    "Crow's Harvest now deals 15% additional damage to "
                    "enemies inside.' The 'inside Deathwind' condition is not "
                    "modellable without zones, so the damage bonus is "
                    "unconditional and smaller. Capped at 2 ranks because "
                    "ability_<id>_duration is flat turns and three extra "
                    "turns would double a 3-turn heal."),
        node(H, "ravenous_thirst", "Ravenous Thirst",
             "Reduces the Mana cost of Ghastly Screech and Soul Strike by 6% "
             "per rank.",
             3, 2, 3, {"ability_reaper_ghastly_screech_cost_pct": 0.06,
                       "ability_reaper_soul_strike_cost_pct": 0.06},
             connect=["genocide"],
             source="CoA: 'Reduces the Runic Power cost of Ghastly Screech "
                    "and Soul Strike by -10.' Flat 10 of a Runic Power bar "
                    "becomes a percentage of a Mana cost that grows with "
                    "rank."),
        node(H, "the_time_has_come", "The Time Has Come",
             "Increases all damage you deal by 2% per rank.",
             3, 3, 3, {"all_damage": 0.02}, connect=["crimson_thirst"],
             source="CoA: 'Your abilities now deal 10% more damage against "
                    "slowed targets.' Nothing reads a target's slow state in "
                    "the damage path, so the condition is dropped and the "
                    "bonus shrinks to match - the spec does run Harvesting "
                    "Grounds and Ghost Claw, so in practice the targets "
                    "usually are slowed."),

        node(H, "hemorrhage", "Hemorrhage",
             "Increases the damage of Slaughter by 8% per rank.",
             4, 0, 3, {"ability_reaper_slaughter_damage": 0.08},
             connect=["souls_for_the_slaughter"], total_slots=3,
             source="CoA: 'Increases the damage and critical strike chance of "
                    "your abilities by 10% against enemies below 35% "
                    "health.' _damage_multiplier has no recipient, so there "
                    "is no way to read the TARGET's health there. Landed on "
                    "Slaughter, which is already gated to 35% - the same "
                    "window, reached honestly."),
        node(H, "crimson_death", "Crimson Death",
             "Your strikes have a 10% chance per rank to repeat Slaughter at "
             "no cost.",
             4, 1, 3, {}, connect=["hungering_scythe"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 1,
                   "cast_ability": "reaper_slaughter"},
             source="CoA: 'Your Slaughter now has a 20% chance to cast an "
                    "additional time free of cost.' cast_ability is a real "
                    "proc payload. Deliberately NOT filtered to Slaughter, "
                    "because Slaughter's own execute gate already decides "
                    "whether the free cast lands - the roll happens on any "
                    "strike and only pays out on a target under 35%."),
        node(H, "harvest_time", "Harvest Time",
             "Teaches Harvest Time: for 3 turns your damage and critical "
             "strike chance both rise by 15%.",
             4, 2, 1, {"unlock_ability": "reaper_harvest_time"},
             node_type="active",
             connect=["ravenous_thirst", "the_time_has_come"], total_slots=3,
             source="CoA: 'Harvest Time (and the Blood Frenzy it unleashes) "
                    "as your burst window when you can commit to a heavy "
                    "trade.'"),

        node(H, "darkrend_scythe", "Darkrend Scythe",
             "Doomrend and Crow's Harvest have a 40% chance per rank to open "
             "a bleed, dealing damage over 3 turns.",
             5, 0, 2, {}, connect=["hemorrhage"], total_slots=3,
             proc=dot_proc("on_damage_cast", 40, "reaper_darkrend_scythe",
                           "Darkrend Scythe", 55, 3, school="physical",
                           abilities=["doomrend", "crows_harvest"]),
             source="CoA: 'Damage dealt by Doomrend and Crow's Harvest now "
                    "applies a bleed, dealing AP Physical damage every 2 sec "
                    "for 10 seconds, stacking 5 times.' Filtered to those two "
                    "abilities exactly as written. Physical-schooled, so it "
                    "reads as a bleed; the 5-stack version is dropped."),
        node(H, "deathbringer", "Deathbringer",
             "Your Harvest Time and Blood Frenzy each last 1 turn longer per "
             "rank.",
             5, 1, 2, {"ability_reaper_harvest_time_duration": 1,
                       "ability_reaper_blood_frenzy_duration": 1},
             connect=["crimson_death"], total_slots=3,
             source="CoA: 'Increases the duration of Blood Frenzy and Harvest "
                    "Time by 100%.' Two ranks on a 3-turn window is close "
                    "enough to doubling it."),
        node(H, "shudder_scythe", "Shudder Scythe",
             "Increases the damage of Murder by 8% and its critical strike "
             "chance by 3% per rank.",
             5, 2, 3, {"ability_reaper_murder_damage": 0.08,
                       "ability_reaper_murder_crit": 3.0},
             connect=["harvest_time"], total_slots=3,
             source="CoA: 'Your Murder is transformed into Shudder Scythe ... "
                    "Strike an enemy 5 times, each dealing 30% Weapon Damage "
                    "... and granting you a Soul Fragment with each strike.' "
                    "An ability transform is not expressible, so the "
                    "transform's upside lands on Murder directly."),

        node(H, "blood_frenzy", "Blood Frenzy",
             "Teaches Blood Frenzy, and increases your physical damage by 8%. "
             "The longer the fight runs, the worse it goes for them.",
             6, 0, 1, {"unlock_ability": "reaper_blood_frenzy",
                       "physical_damage": 0.08},
             node_type="active",
             connect=["darkrend_scythe", "deathbringer", "shudder_scythe"],
             total_slots=1,
             source="Capstone. CoA puts Blood Frenzy at its own top tier, "
                    "'your all-in button for extended trades' - and the spec "
                    "blurb is literally 'The longer the fight runs, the worse "
                    "it goes for the enemy', which is why the capstone is "
                    "sustained damage rather than a burst window."),
    ],
    "Built from reference/coa_sidekick/SPEC_reaper__harvest.txt: 'Closest to "
    "Blood Death Knight ... Your own damage is your healing, packaged in an "
    "AoE cleave-and-leech loop.' CoA rates it PvE B / PvP C and recommends it "
    "for levelling. The tree spends most of its points on the three things "
    "the reference says carry the spec - the Harvester leech, Doomrend's "
    "anti-heal, and the Slaughter execute - and the reference's own named "
    "weakness ('No blink, no vanish, no bubble, no CC-break in the spec "
    "line') is honoured by leaving every defensive out in the class kit.")


# ================================================================== Soul
S = "reaper_soul"
SOUL = tree(
    S, "Reaper Soul",
    "Shadowfrost duelist - weapon strikes feed the soul magic, the soul "
    "magic heals you back, and Limbo and Shade are two separate ways out of "
    "a fight that has turned.",
    [
        node(S, "mark_of_death", "Mark of Death",
             "Increases the damage of Deathchaser by 4% and your hit rating "
             "by 1 per rank.",
             0, 0, 5, {"ability_reaper_deathchaser_damage": 0.04,
                       "hit_rating": 1},
             source="CoA: 'Increases the damage dealt by Deathchaser by 15% "
                    "and your hit chance by 3%.' The spec's stat priority "
                    "leads with Spell Hit 'until your Shadow spells stop "
                    "missing a +3-level target', so the hit is not filler."),
        node(S, "ghostly_magic", "Ghostly Magic",
             "Increases the damage of Reap, Dirge and Reliquary of the Lost "
             "by 3% per rank.",
             0, 1, 5, {"ability_reaper_reap_damage": 0.03,
                       "ability_reaper_dirge_damage": 0.03,
                       "ability_reaper_reliquary_of_the_lost_damage": 0.03},
             source="CoA: 'Increases the damage of Reap, Dirge, and Reliquary "
                    "of the Lost by 10%', 2 ranks - the three buttons the "
                    "rotation actually presses."),
        node(S, "spirit_render", "Spirit Render",
             "Increases your Shadow spell damage by 2% per rank.",
             0, 2, 5, {"shadow_spell_damage": 0.02},
             source="CoA's level-20 free passive: 'Increases your spell "
                    "penetration by 20, scaling with your level.' There is no "
                    "spell-penetration stat here, and the effect of "
                    "penetration is more Shadow damage landing, so that is "
                    "what it grants. shadow_spell_damage is built at runtime "
                    "as f'{school}_spell_damage' - a grep for the literal "
                    "finds nothing and calls it dead; it is not."),
        node(S, "spirit_chaser", "Spirit Chaser",
             "Increases the critical strike chance of Reap, Deathchaser and "
             "Wraithblade by 2% per rank.",
             0, 3, 5, {"ability_reaper_reap_crit": 2.0,
                       "ability_reaper_deathchaser_crit": 2.0,
                       "ability_reaper_wraithblade_crit": 2.0},
             source="CoA: 'Increases the critical strike chance and critical "
                    "damage of Reap, Deathchaser, and Wraithblade by 10%.' "
                    "The crit-damage half is dropped; Perfect-Pitch-style "
                    "crit damage would overlap Gravesite at the capstone."),

        node(S, "soul_generator", "Soul Generator",
             "Your critical strikes have a 25% chance per rank to harvest a "
             "Soul.",
             1, 0, 3, {}, connect=["mark_of_death"],
             proc=soul_proc("on_crit", 25, 12),
             source="CoA: 'Critical strikes with Dirge now generate 10 Runic "
                    "Power. Critical strikes with Murder now generate 1 "
                    "additional Reaped Soul.' Collapsed to one crit-to-Souls "
                    "proc, unfiltered, since both halves do the same job."),
        node(S, "shattered_souls", "Shattered Souls",
             "Increases the damage of Wraithblade by 8% per rank.",
             1, 1, 3, {"ability_reaper_wraithblade_damage": 0.08},
             connect=["ghostly_magic"],
             source="CoA: 'Your Wraithblade now deals double damage to "
                    "enemies affected by Soulrend.' A conditional double is "
                    "not expressible - nothing reads the target's debuffs in "
                    "the damage path - so it is a flat Wraithblade bonus."),
        node(S, "deathwail", "Deathwail",
             "Reduces the Mana cost of Wraithblade by 8% per rank.",
             1, 2, 3, {"ability_reaper_wraithblade_cost_pct": 0.08},
             connect=["spirit_render"],
             source="CoA: 'Reduces the Runic Power cost of Wraithblade by "
                    "-50%.' Three ranks of 8% rather than half the cost in "
                    "one node."),
        node(S, "death_dealer", "Death Dealer",
             "Your Ghostly Weapon and Soulrend each last 1 turn longer per "
             "rank.",
             1, 3, 2, {"ability_reaper_ghostly_weapon_duration": 1,
                       "ability_reaper_soulrend_duration": 1},
             connect=["spirit_chaser"],
             source="CoA: 'Increases the duration of Ghostly Weapon and "
                    "Soulrend by 5 sec.'"),

        node(S, "weakened_souls", "Weakened Souls",
             "Your Soulrend leaves the target taking 10% more Shadow and "
             "Frost damage.",
             2, 0, 1, {}, connect=["soul_generator"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                   "ability_filter": ["reaper_soulrend"],
                   "apply_effect": {
                       "effect_id": "reaper_weakened_soul",
                       "name": "Weakened Soul",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"shadow_damage_taken_pct": 10.0,
                                     "frost_damage_taken_pct": 10.0},
                       "on_target": True}},
             source="CoA's level-10 free passive: 'Your Soulrend now also "
                    "applies Weakened Soul, increasing the target's Shadow "
                    "and Frost damage taken from you by 10%.' Literal, "
                    "filtered to Soulrend. 'From you' is lost - a debuff on "
                    "the target applies to everyone's hits. One point, "
                    "because a 100% proc's payload cannot scale with rank. "
                    "<school>_damage_taken_pct in a debuff is POINTS."),
        node(S, "essence_harvest", "Essence Harvest",
             "Increases your Frost spell damage by 3% per rank.",
             2, 1, 3, {"frost_spell_damage": 0.03},
             connect=["shattered_souls"],
             source="CoA: 'Increases the additional Frost damage dealt by "
                    "Ghostly Weapon by 10%.' Ghostly Weapon's added Frost "
                    "damage does not exist as a mechanic here, so this scales "
                    "the Frost half of Deathchaser and Ghastly Screech "
                    "instead - both really are Shadowfrost."),
        node(S, "soulbender", "Soulbender",
             "Reduces the cooldown of Deathchaser by 1 turn per rank.",
             2, 2, 2, {"ability_reaper_deathchaser_cooldown": 1},
             connect=["deathwail"],
             source="CoA: 'Significantly increases the Runic Power generated "
                    "by Deathchaser.' No talent key raises an ability's "
                    "`generates` amount, so more uptime stands in for more "
                    "resource: a shorter cooldown means more Deathchaser "
                    "casts and therefore more Souls."),
        node(S, "purgatory", "Purgatory",
             "Increases the damage of Soulrend and Reliquary of the Lost by "
             "4% per rank.",
             2, 3, 5, {"ability_reaper_soulrend_damage": 0.04,
                       "ability_reaper_reliquary_of_the_lost_damage": 0.04},
             connect=["death_dealer"],
             source="CoA: 'When you gain Soul Infusion, the damage of your "
                    "Soulrend and Reliquary of the Lost is increased by 20% "
                    "for 6 seconds, stacking 2 times.' The ramp needs a "
                    "resource-gain trigger the engine does not have, so the "
                    "20% is permanent and spread over 5 ranks."),

        node(S, "spectres_call", "Spectre's Call",
             "Increases the damage of Murder and Soul Strike by 3%, and the "
             "healing of Deathwind by 3%, per rank.",
             3, 0, 5, {"ability_reaper_murder_damage": 0.03,
                       "ability_reaper_soul_strike_damage": 0.03,
                       "ability_reaper_deathwind_healing": 0.03},
             connect=["weakened_souls"],
             source="CoA: 'Increases the damage of Deathwind, Murder, and "
                    "Soul Strike by 15%.' Deathwind is a heal here, so it "
                    "takes the _healing key - ability_<id>_healing was dead "
                    "for 18 talents until _damage_multiplier started reading "
                    "it, and _damage on a heal still does nothing."),
        node(S, "apparition", "Apparition",
             "Increases the damage of Spectre Stride by 10% per rank.",
             3, 1, 3, {"ability_reaper_spectre_stride_damage": 0.10},
             connect=["essence_harvest"],
             source="CoA: 'Increases the damage of Spectre Stride by 30% and "
                    "reduces the chance for enemies to see you while "
                    "stealthed.' The stealth half has no hook."),
        node(S, "anima_ambusher", "Anima Ambusher",
             "Your Spectre Stride has a 40% chance per rank to leave Shadow "
             "rot on the target for 3 turns.",
             3, 2, 3, {}, connect=["soulbender"],
             proc=dot_proc("on_damage_cast", 40, "reaper_anima_ambusher",
                           "Anima Ambusher", 60, 3,
                           abilities=["spectre_stride"]),
             source="CoA: 'Spectre Stride now deals an additional 125% of its "
                    "damage dealt over 5 seconds.' A dot sized off the "
                    "triggering hit is not expressible through apply_effect, "
                    "so the potency is flat. Filtered to Spectre Stride."),
        node(S, "fleeting_soul", "Fleeting Soul",
             "Reduces the cooldown of Soulslam by 1 turn per rank.",
             3, 3, 3, {"ability_reaper_soulslam_cooldown": 1},
             connect=["purgatory"],
             source="CoA: 'Reduces the cooldown of Soulslam by -15 sec.'"),

        node(S, "spiritual_reflexes", "Spiritual Reflexes",
             "Increases your dodge chance by 1% per rank, and while below 35% "
             "health you take a further 5% less damage per rank.",
             4, 0, 3, {"dodge": 1.0, "low_health_damage_reduction_pct": 0.05},
             connect=["spectres_call"], total_slots=3,
             source="CoA: 'While below 35% maximum health, your chance to "
                    "dodge attacks is increased by 25% and dodging an attack "
                    "unleashes Soul Harvest on the target.' Dodge cannot be "
                    "made conditional - it is a plain derived stat - so the "
                    "dodge is unconditional and smaller while the "
                    "below-35% clause carries real mitigation through the "
                    "engine's existing low-health pair. The 35% threshold is "
                    "the engine default and is NOT authored here: "
                    "low_health_threshold_pct is multiplied by points spent, "
                    "so a 3-rank node carrying 0.35 would reach 1.05 and "
                    "count the character as low on health at full HP."),
        node(S, "soul_piercer", "Soul Piercer",
             "Your strikes have a 20% chance per rank to refund a Soul.",
             4, 1, 3, {}, connect=["apparition", "anima_ambusher"],
             total_slots=3, proc=soul_proc("on_damage_cast", 20, 10, icd=1),
             source="CoA: 'Striking at least 1 enemy with Soulslam now "
                    "refunds its Reaped Souls.' A full refund on the spec's "
                    "big spender would make the Souls pool meaningless, so it "
                    "is a chance-based partial refund off any strike, with a "
                    "1 turn internal cooldown."),
        node(S, "deaths_presence", "Death's Presence",
             "Teaches Death's Presence: your party and raid deal 3% more "
             "damage.",
             4, 2, 1, {"unlock_ability": "reaper_deaths_presence"},
             node_type="active", connect=["fleeting_soul"], total_slots=3,
             source="CoA: 'Death's Presence, a static party damage buff, is "
                    "the entire party toolkit.' Costing a talent point for it "
                    "is how CoA has it too."),

        node(S, "lord_of_death", "Lord of Death",
             "Increases the damage your abilities deal to additional targets "
             "by 10% per rank.",
             5, 0, 3, {"aoe_damage": 0.10}, connect=["spiritual_reflexes"],
             total_slots=3,
             source="CoA: 'Abilities affected by Ghostly Weapon now deal 25% "
                    "more damage per additional target', and Ghastly Hilt "
                    "'causes your melee abilities to strike up to 2 "
                    "additional targets'. Both collapse into the engine's "
                    "aoe_damage key, which is what 'Strong AoE/cleave for "
                    "trash packs' needs."),
        node(S, "the_end_is_near", "The End Is Near",
             "Your Wraithblade has a 35% chance per rank to strike a second "
             "time.",
             5, 1, 2, {}, connect=["soul_piercer"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 35, "icd": 0,
                   "ability_filter": ["reaper_wraithblade"],
                   "extra_attack": 1},
             source="CoA: 'Wraithblade now creates a spectral version of "
                    "yourself for 12 seconds that casts Dirge and Murder on "
                    "enemies.' There is no temporary-clone primitive, and a "
                    "pet template would be a different thing; extra_attack is "
                    "a real second swing off the same cast, which is the "
                    "honest small version of a copy of you swinging too."),
        node(S, "beyond_the_veil", "Beyond the Veil",
             "Increases your haste by 2 and your dodge chance by 1% per rank.",
             5, 2, 2, {"haste": 2.0, "dodge": 1.0},
             connect=["deaths_presence"], total_slots=3,
             source="CoA's level-40 free passive: 'increasing movement speed "
                    "by 30% and allowing you to walk on water.' Neither "
                    "movement speed nor water-walking exists in combat, so "
                    "the node becomes the mobility stats a turn engine can "
                    "express. The weakest translation in the class and "
                    "recorded as such."),

        node(S, "endbringer", "Endbringer",
             "Teaches Endbringer, and increases your critical strike damage "
             "by 15%. For a while, you are the last thing that happens here.",
             6, 0, 1, {"unlock_ability": "reaper_endbringer",
                       "crit_damage_spell": 0.15},
             node_type="active",
             connect=["lord_of_death", "the_end_is_near", "beyond_the_veil"],
             total_slots=1,
             source="Capstone. CoA puts Endbringer and Gravesite on the same "
                    "top tier ('Casting Endbringer now marks the ground "
                    "beneath you as your Gravesite ... Direct critical "
                    "strikes made against enemies within a Gravesite now "
                    "deals AP Shadow damage'), so the node teaches the "
                    "cooldown and carries Gravesite's crit payoff as spell "
                    "crit damage rather than a ground effect."),
    ],
    "Built from reference/coa_sidekick/SPEC_reaper__soul.txt: 'Closest to "
    "retail Vengeance Demon Hunter. The Soul Fragment into "
    "consume-for-self-heal loop is nearly identical in shape ... It's "
    "Vengeance's fragment engine wearing a rogue-flavored "
    "stealth-and-mobility duelist chassis.' CoA rates it Dungeon A / Raid C. "
    "The tree is deliberately the most magical of the three: its stat "
    "priority opens with Spell Hit and the reference's own summary is that it "
    "heals 'off your own fragment generation' with 'No dedicated heal spell "
    "anywhere', which is why the Shadow and Frost damage nodes are load "
    "bearing rather than flavour.")


# ============================================================= Domination
D = "reaper_domination"
DOMINATION = tree(
    D, "Reaper Domination",
    "Attrition tank - mitigation layers that deepen the longer the fight "
    "runs, Souls spent on bodies and sustain instead of burst, and real "
    "party cooldowns from a tank.",
    [
        node(D, "dreadknight", "Dreadknight",
             "Increases your Armor by 3% per rank.",
             0, 0, 5, {"armor_pct": 3.0},
             source="CoA: 'Increases your armor contribution from mail and "
                    "plate items by 20% and reduces the chance for spells to "
                    "hit you by -2%.' Armour-by-item-type is not a thing "
                    "here, and spell miss on the defender has no key, so it "
                    "is flat Armor. armor_pct is percentage POINTS."),
        node(D, "dark_soldier", "Dark Soldier",
             "Increases your hit rating by 1 and reduces the Magic damage you "
             "take by 1% per rank.",
             0, 1, 5, {"hit_rating": 1, "magic_damage_taken_pct": -0.01},
             source="CoA: 'Increases your hit chance by 3% and reduces your "
                    "Magic damage taken by -2%.' Both halves are literal. The "
                    "spec's stat priority opens Hit > Expertise, so the hit "
                    "is the point. magic_damage_taken_pct as a TALENT effect "
                    "is a FRACTION, the opposite of the same key in a buff."),
        node(D, "empyrean_fortitude", "Empyrean Fortitude",
             "Increases your parry chance by 1% per rank.",
             0, 2, 5, {"parry": 1.0},
             source="CoA: 'Increases your parry chance by 5% and parrying an "
                    "attack now generates 2 Runic Power.' There is no "
                    "on-parry trigger, so the resource half is lost - Soul "
                    "Slip below covers avoidance-into-resource as best the "
                    "engine allows."),
        node(D, "behemoth", "Behemoth",
             "Increases your Stamina by 2% per rank.",
             0, 3, 5, {"stamina_pct": 2.0},
             source="CoA's level-20 free passive: 'Increases your Stamina by "
                    "20% and your Armor penetration by 10% of your Strength.' "
                    "Stamina is kept at the shipped 2%/rank; Dark Soul's "
                    "armour-penetration-into-Stamina loop is dropped because "
                    "it has no conversion source."),

        node(D, "dominator", "Dominator",
             "Reduces the Mana cost of Soul Strike by 6% per rank.",
             1, 0, 3, {"ability_reaper_soul_strike_cost_pct": 0.06},
             connect=["dreadknight"],
             source="CoA: 'Reduces the Runic Power cost of Soul Strike.' No "
                    "number given in the reference, so it takes the same "
                    "6%/rank every other cost node in this class uses."),
        node(D, "lifestealer", "Lifestealer",
             "Increases the healing Soul Strike does by 8% per rank.",
             1, 1, 3, {"ability_reaper_soul_strike_healing": 0.08},
             connect=["dark_soldier"],
             source="CoA: 'Increases the missing health generated by Soul "
                    "Strike by 3%.' Scaling with the caster's own missing "
                    "health is not expressible, so it is a flat boost to the "
                    "leech - which is the same thing when you are being hit."),
        node(D, "jailers_will", "Jailer's Will",
             "Increases the damage of Soul Strike by 8% per rank.",
             1, 2, 3, {"ability_reaper_soul_strike_damage": 0.08},
             connect=["empyrean_fortitude"],
             source="CoA: 'Soul Strike now deals 30% Strength increased "
                    "damage, scaling with Strength.' Soul Strike resolves on "
                    "the spell path (damage_and_heal), so a Strength scalar "
                    "would not reach it; a flat damage bonus does."),
        node(D, "soultaker", "Soultaker",
             "Reduces the cooldown of Tormented Souls by 1 turn per rank.",
             1, 3, 3, {"ability_reaper_tormented_souls_cooldown": 1},
             connect=["behemoth"],
             source="CoA: 'Damage dealt with Dreadwake now reduces the "
                    "cooldown of Tormented Souls by -1 sec', and Tormentor's "
                    "'Consuming Soul Infusion now reduces the cooldown of "
                    "Tormented Souls'. A flat reduction stands in for both "
                    "- there is no on-cast cooldown-shaving hook."),

        node(D, "soul_slip", "Soul Slip",
             "Blows that land on you have a 25% chance per rank to shake a "
             "Soul loose from the attacker.",
             2, 0, 3, {}, connect=["dominator"],
             proc=soul_proc("on_damage_taken", 25, 10),
             source="CoA's level-30 free passive: 'Avoiding attacks now has a "
                    "50% chance to harvest a Soul Fragment from the "
                    "attacker.' There is no on-avoid trigger - the engine "
                    "dispatches on_damage_taken, which fires when a hit "
                    "LANDS, the opposite case - so the tooltip is worded for "
                    "what actually happens rather than for what CoA says."),
        node(D, "fatesealer", "Fatesealer",
             "Reduces all damage you take by 2% per rank.",
             2, 1, 3, {"damage_taken_pct": -0.02}, connect=["lifestealer"],
             source="CoA: 'Generating a Reaped Soul now reduces damage taken "
                    "by -2% for 15 seconds, stacking 3 times.' Three stacks "
                    "of 2% becomes three ranks of 2%, always on - the ramp "
                    "needs a resource-gain trigger the engine lacks. This is "
                    "the flat-mitigation node the reference's 'Bursting you "
                    "down is not realistic' depends on."),
        node(D, "soul_knight", "Soul Knight",
             "Reduces the Magic damage you take by 2% per rank.",
             2, 2, 3, {"magic_damage_taken_pct": -0.02},
             connect=["jailers_will"],
             source="CoA: 'Your successful parries and dodges increase all "
                    "healing you receive by 2% and reduce all Magic damage "
                    "taken by -2% for 10 seconds, stacking 5 times.' "
                    "healing_taken_pct is read ONLY through "
                    "get_status_stat_mod and never get_talent_effect, so the "
                    "healing-received half would be a dead talent; only the "
                    "magic reduction survives, unconditionally."),
        node(D, "soul_splinters", "Soul Splinters",
             "Your strikes have a 25% chance per rank to erupt, rotting the "
             "target for 2 turns.",
             2, 3, 3, {}, connect=["soultaker"],
             proc=dot_proc("on_damage_cast", 25, "reaper_soul_splinters",
                           "Soul Splinters", 50, 2),
             source="CoA: 'Erupt with ghastly force whenever you harvest a "
                    "Reaped Soul, dealing AP Spellshadow Damage to nearby "
                    "enemies over 6 seconds.' A proc cannot hit 'nearby "
                    "enemies' without splash_damage, which no shipped tree "
                    "uses, so it is a single-target Shadow dot on the thing "
                    "you just hit."),

        node(D, "soulstorm", "Soulstorm",
             "Your Requiem and Soulrend leave enemies attacking 20% slower "
             "for 3 turns.",
             3, 0, 1, {}, connect=["soul_slip"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                   "ability_filter": ["reaper_requiem", "reaper_soulrend"],
                   "apply_effect": {
                       "effect_id": "reaper_soulstorm_slow",
                       "name": "Requiem",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"haste": -20.0},
                       "on_target": True}},
             source="CoA: 'Requiem and Soulrend now have a 40% chance to "
                    "refund a Reaped Soul.' Reassigned: Requiem's OWN "
                    "attack-speed slow ('reducing their melee and ranged "
                    "attack speed by 20% for 15 seconds') could not ride on "
                    "the ability, because only buff and debuff abilities "
                    "carry a proc and Requiem has to deal damage. This node "
                    "gives it back, filtered to the two abilities CoA names. "
                    "One point - a 100% proc's payload cannot scale."),
        node(D, "intimidating_presence", "Intimidating Presence",
             "Increases your threat generation by 6% per rank.",
             3, 1, 3, {"threat_generation_pct": 0.06},
             connect=["fatesealer"],
             source="CoA: 'Bolstered Form now increases the damage nearby "
                    "enemies take from you by 15% for 15 seconds.' Reading "
                    "as the threat node the tank tree needs - CoA calls the "
                    "spec a 'Strong dungeon tank - AoE pulls and threat'. "
                    "threat_generation_pct as a TALENT effect is a FRACTION, "
                    "and as an ability buff's stat_mod it is percentage "
                    "POINTS; the same key, two conventions."),
        node(D, "hard_bargain", "Hard Bargain",
             "Increases your haste by 1 and reduces the Mana cost of "
             "Dreadwake by 6% per rank.",
             3, 2, 3, {"haste": 1.0,
                       "ability_reaper_dreadwake_cost_pct": 0.06},
             connect=["soul_knight"],
             source="CoA: 'While Tormented Souls is active on you, your melee "
                    "attack speed is increased by 30% and your Dreadwake "
                    "costs -5 less Runic Power.' Nothing gates a talent on "
                    "another effect being active, so both halves are "
                    "unconditional and smaller. Also carries the personal "
                    "haste Ethereal Guard had to drop."),
        node(D, "essence_binder", "Essence Binder",
             "Increases your Strength by 2% per rank.",
             3, 3, 3, {"strength_pct": 2.0}, connect=["soul_splinters"],
             source="CoA: 'Soul Strike now steals some of the target's health "
                    "and Strength for 12 seconds, granting it to you at "
                    "increased value.' A steal needs to read and modify the "
                    "target's stats; the Strength you end up with is the part "
                    "that is expressible. strength_pct is percentage POINTS."),

        node(D, "spirit_realm", "Spirit Realm",
             "Increases the healing your Deathwind does by 8% per rank.",
             4, 0, 3, {"ability_reaper_deathwind_healing": 0.08},
             connect=["soulstorm"], total_slots=3,
             source="CoA: 'Your Deathwind now also increases your healing "
                    "taken by 10% while you stand within its radius', and "
                    "Eater of Souls' 'healing done by Deathwind is increased "
                    "by 10%'. No radius, so both become a straight boost to "
                    "Deathwind's own healing."),
        node(D, "well_of_souls", "Well of Souls",
             "Reduces the cooldown of Spectral Scythe by 1 turn per rank.",
             4, 1, 3, {"ability_reaper_spectral_scythe_cooldown": 1},
             connect=["intimidating_presence", "hard_bargain"], total_slots=3,
             source="CoA: 'Damage dealt by Soul Strike and Murder now reduces "
                    "the cooldown of Spectral Scythe by -1 sec.' A flat "
                    "reduction rather than an on-hit shave."),
        node(D, "ethereal_guard", "Ethereal Guard",
             "Teaches Ethereal Guard: your party and raid take 3% less "
             "damage.",
             4, 2, 1, {"unlock_ability": "reaper_ethereal_guard"},
             node_type="active", connect=["essence_binder"], total_slots=3,
             source="CoA: 'Ethereal Guard cuts raid-wide damage ... Rare "
                    "support from a tank.' Costs a point, as it does in CoA."),

        node(D, "spirit_culling", "Spirit Culling",
             "Increases the damage your Spectral Scythes and Wardens deal by "
             "6% per rank.",
             5, 0, 3, {"pet_damage": 0.06}, connect=["spirit_realm"],
             total_slots=3,
             source="CoA: 'For the duration of Spectral Scythe, the damage of "
                    "Soul Strike is increased by 20%. In addition, generating "
                    "a Reaped Soul now has a 10% chance to summon a Spectral "
                    "Scythe.' Neither half is expressible, so the node scales "
                    "the summons themselves through pet_damage - a key built "
                    "at runtime and listed in audit_talents._NAMED_LIVE."),
        node(D, "painmail", "Painmail",
             "Blows that land on you have a 40% chance per rank to knit you "
             "back together.",
             5, 1, 3, {}, connect=["well_of_souls"], total_slots=3,
             proc={"trigger": "on_damage_taken", "chance": 40, "icd": 0,
                   "heal_flat": 70},
             source="CoA: 'Dealing damage with Reap, Dreadwake and Soul "
                    "Strike now grants a stack of Painmail ... When Painmail "
                    "stacks expire naturally, you are healed for 2% of your "
                    "maximum health and reduce the cooldown of Bolstered Form "
                    "by -0.5 sec for each stack.' Nothing fires on a stack "
                    "EXPIRING, so the heal is moved to the moment it is "
                    "needed instead - taking a hit."),
        node(D, "spirit_army", "Spirit Army",
             "Teaches Spectral Warden: a body that fights beside you.",
             5, 2, 1, {"unlock_ability": "reaper_spectral_warden"},
             node_type="active", connect=["ethereal_guard"], total_slots=3,
             source="CoA: 'Your Spectral Warden now causes you to summon 2 "
                    "additional Spectral Wardens ... increases the amount "
                    "absorbed by the shield granted by Spectral Warden by "
                    "100%.' One body rather than three, and no group absorb - "
                    "summon_pet summons one pet and does nothing else."),

        node(D, "eater_of_souls", "Eater of Souls",
             "Teaches Eater of Souls, and permanently reduces the physical "
             "damage you take by 5% and raises your health by 5%.",
             6, 0, 1, {"unlock_ability": "reaper_eater_of_souls",
                       "physical_damage_taken_pct": -0.05,
                       "max_health_pct": 0.05},
             node_type="active",
             connect=["spirit_culling", "painmail", "spirit_army"],
             total_slots=1,
             source="Capstone. CoA puts Eater of Souls on its top tier and "
                    "the playstyle page builds the whole rotation around it: "
                    "'Hold Reaped Souls to bank the Eater of Souls proc "
                    "before you dump them into Spectral Scythe.' NOTE "
                    "max_health_pct is a FRACTION - health * (1 + value) - "
                    "so 0.05 is +5%. Guardian shipped 2.0 on this key and "
                    "granted +200% a rank, reaching 99,156 effective HP "
                    "against the next tank's 2,987; physical_damage_taken_pct "
                    "as a TALENT effect is a fraction too, unlike the same "
                    "key in a buff."),
    ],
    "Built from reference/coa_sidekick/SPEC_reaper__domination.txt: 'Closest "
    "to Vengeance Demon Hunter ... The one piece that isn't pure Vengeance is "
    "the support tilt. Ethereal Guard and Soulsight hand out raid-wide damage "
    "reduction and crit, leaning Blood-DK-style toughness-and-anchor onto the "
    "DH-shaped chassis.' CoA rates it Dungeon A / Raid B and Arena D. The "
    "tree spends almost nothing on burst, because the reference is explicit "
    "that there is none - 'No instant burst and no finisher. Everything is "
    "builder, DoT and cleave, so you swing fights by attrition and "
    "mitigation' - and instead stacks four separate mitigation keys "
    "(damage_taken_pct, magic_damage_taken_pct, physical_damage_taken_pct, "
    "armor_pct) so the layering the reference describes is real.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Reaper",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/reaper.json", ability_doc),
        (ROOT / "data/talents/reaper_harvest.json", HARVEST),
        (ROOT / "data/talents/reaper_soul.json", SOUL),
        (ROOT / "data/talents/reaper_domination.json", DOMINATION),
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
