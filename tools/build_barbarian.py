#!/usr/bin/env python3
"""Author the Barbarian: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_barbarian.py [--apply]

Barbarian is one of the twelve CoA classes that shipped with base stats,
armour type, weapon proficiency and a resource but no abilities and no
talents, which left it unselectable. Written as a sibling of
tools/build_guardian.py and following its structure, helpers and _source
discipline.

SOURCE. reference/coa_sidekick/CLASS_barbarian.txt, the three
SPEC_barbarian__*.txt pages, and reference/coa_sidekick/talents/
barbarian.json (the real talent list, scraped from ascensionsidekick.com).
Every ability and talent name below is a real CoA name off those pages.
Identity per that reference:

  Brutality    MELEE DPS      "Closest to retail Fury Warrior, but with
                              Second-Wind-style self-healing built into the
                              rotation instead of bolted on." An Enrage
                              engine: Smash needs an active enrage, the spec
                              carries three, and Decapitate executes below
                              35%.
  Headhunting  RANGED DPS     "Closest to retail Survival Hunter with a
                              Feral Druid's survivability bolted on." Thrown
                              weapons and bleeds, with the Born in Blood
                              heal-over-time generated off its own crits.
  Ancestry     MELEE DPS /    "Closest to retail Enhancement Shaman." A
               SUPPORT        Frost/physical brawler behind a wall of
                              always-on party auras, with a summoned
                              ancestor and a party haste cooldown.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference gives identity, role and
rotation shape; it is a fan-made planning tool whose own disclaimer says COA
is pre-meta. Damage curves copy the shipped Warrior/Guardian shape
(heroic_strike: 9 ranks at levels 1/6/12/18/24/32/40/48/56, flat resource
cost, linear growth) because Guardian is the other Energy melee class and
the two should scale alongside each other rather than on curves of their own
invention.

ENERGY BUDGET. CLASS_RESOURCE_MAP gives Barbarian (ENERGY, None) - no
secondary pool. 100 cap, +25/turn in combat (Character.
restore_resources_between_turns), so costs are flat across ranks like the
Rogue's and Guardian's and sized against 25/turn: ~15-20 filler, ~25-30
dump, ~35 payoff. A cost over 100 would make an ability uncastable forever.

FROST ON A CLASS WITH NO MAGIC. CoA calls the Barbarian "simple of mind and
with no magic of their own", yet Ancestry's whole kit deals Frost - and CoA
is explicit about where that Frost comes from: Ale of the God-King and
Clanlord's Totem both scale "with your attack power". This engine only
routes a real damage school through effect_type="spell_damage"/"spell_dot"
(effect_type="damage" is hardcoded physical in _apply_effect), and
spell_damage scales off get_effective_spell_power. So Ancestry's Frost
abilities are spell_damage with damage_school="frost", and the tree carries
Frozen Warlord (spell_power_from_ap_pct), the real conversion key that turns
the Barbarian's attack power into the spell power those casts read. Without
that node the Frost half of the spec runs on its flat effect_value alone.

Talent effect keys are restricted to ones the engine actually reads -
verified with tools/validate_class.py, which delegates liveness to
tools/audit_talents.py. Gaps where CoA describes a mechanic this engine
cannot express are recorded in the node's own _source rather than papered
over with a plausible-looking dead key. The recurring ones:

  no enrage tag      Smash "requires an active Enrage", Berserker Axe and
                     Ancestral Roar are enrage-gated, and three abilities
                     exist mainly to BE enrages. There is no enrage state in
                     this engine and no requires_buff field, so those gates
                     are dropped and the enrages are ordinary buffs.
  no second resource Ancestry's Tankard/Fill Level is a real builder with
                     empty-vs-full gating (Breath of the North needs empty,
                     Ale of the God-King needs full). CLASS_RESOURCE_MAP
                     gives Barbarian no secondary pool, so the Tankard is
                     gone; Fill Level lands as energy_max and Liquid
                     Courage's per-stack mitigation as flat mitigation.
  no party talents   Ancestry's auras (Ancestral Wisdom, Frozen Blades,
                     Manhunter, Uniting Voice) buff the party from a TALENT.
                     Talent effects only ever apply to their owner, so the
                     party-facing ones are cast abilities with
                     target_type="party" and the talent versions grant the
                     Barbarian its own share.
  monster stat_mods  Monster reads only `armor` and `attack_power` out of a
                     status effect's stat_mods (entities/monster.py). A
                     debuff authored with physical_damage_taken_pct, a
                     cast-speed slow or a haste snare does nothing to an
                     enemy, so Wounded, Break, Blind Stupor and Maiming
                     Spear carry armour or attack-power shred instead.
  one CC category    There is no silence, root or snare - status_effects.py
                     says so ("one mechanic, is_stun, with no separate
                     silence/root category"). Jawbreaker's interrupt and
                     Skull Smash's disorient are both is_stun, kept to one
                     turn so neither is better than CoA's.
  no execute gate    execute_threshold_pct cannot be used against a monster
                     at all - see Decapitate's own note. Three engine bugs
                     found while writing this, all recorded where they bit:
                     that one, effect_value's silent zeroing of buff
                     stat_mods (see one()), and restore_resource reading a
                     separate rank key (see restore()).

NON-OBVIOUS UNITS, all verified against the code rather than the key name:
  ability stat_mods  scaled by effect_value/100 before anything reads them,
                     so every buff and debuff here carries effect_value 100.
  damage_taken_pct   FRACTION in a stat_mod (-0.3 = -30%); read raw by
                     take_damage's taken_mult.
  max_health_pct     FRACTION (0.15 = +15%); health * (1.0 + value).
  haste, crit, block PERCENT POINTS, added straight onto the derived stat.
  armor_pct,         PERCENT POINTS, divided by 100 where they are read.
  attack_power_pct,
  armor_penetration_pct, strength/stamina/agility/spirit_pct
  physical_ and      PERCENT POINTS from a STAT_MOD (/100), but FRACTIONS
  magic_damage_      from a TALENT effect. The same key, two conventions,
  taken_pct          depending on where it is authored.
  threat_generation  FRACTION as a talent effect, PERCENT POINTS as a
                     stat_mod.
  execute_threshold  PERCENT POINTS (35, not 0.35).
  target_type        "enemy_aoe" is what makes an ability hit a pack.
                     `is_aoe` is not read by _ability_from_data at all.
  buff_scope         only ever "raid" or "combat", and it chooses DURATION
                     (wall clock vs turns), not who gets the buff. A party
                     buff needs target_type="party"; buff_scope="party"
                     normalises to "raid" and lands on the caster alone.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Warrior's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, step, cost, start=1, count=9):
    """Flat-cost rank table on the Warrior schedule, starting at `start`.

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


def one(level, cost, value=100):
    """Single-rank table, for cooldowns and auras that do not scale.

    effect_value DEFAULTS TO 100 and that default is load-bearing. A
    buff/debuff ability's stat_mods are not applied as authored: both
    branches of _apply_effect scale every mod by `effect_value / 100.0`, so
    the authored numbers are a magnitude that a rank table dials from 0 to
    100%. Shipped single-rank buffs (warrior_battle_shout, rogue_cold_blood,
    druid_enrage, ...) all carry effect_value 100 for exactly this reason,
    and a buff authored with 0 silently grants nothing at all while looking
    completely correct in the data and in the validator.
    """
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def restore(level, cost, pct):
    """Single-rank table for effect_type="restore_resource".

    The restored amount comes off a SEPARATE rank key, mana_restore_pct, not
    off effect_value - see Ability.mana_restore_pct. Every shipped
    restore_resource ability (warrior_bloodrage, druid_enrage,
    cultist_sanity_tap, tinker_battery_reclaimer) carries both keys, and one
    authored with only effect_value restores nothing.
    """
    return [{"rank": 1, "level_req": level, "cost": cost,
             "effect_value": 100, "mana_restore_pct": pct}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            # icon=None, NOT "ability_melee". The old default stamped an
            # explicit icon_id of "ability_melee" onto every ability that
            # did not override it, which put 20 of Barbarian's 46 on one
            # shared generic sword - its basic swing, its execute, its
            # cleave and all five thrown-spear abilities drawing the same
            # picture, and the same picture as 190 other abilities across
            # the game. An explicit icon_id WINS over the filename
            # fallback, so those 20 would have kept the sword even after
            # their real art landed in assets/icons/abilities/. None lets
            # icon_migration_and_ui.py fall back to the ability_id, which
            # is what the art is named after. See
            # tools/fetch_coa_icons.py and tools/audit_icon_coverage.py.
            duration=0, stat_mods=None, icon=None, source=None,
            **extra):
    out = {
        "ability_id": f"barbarian_{aid}",
        "name": name,
        "resource_type": "energy",
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
# Order is roughly the order a player meets them. CoA grants most of these
# through class-tree and spec-tree picks; Frontier has no shared class tree,
# so everything CoA spends a point to LEARN is an ability here and only the
# passives become talents.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A measured swing with your weapon.", one(1, 0, 0),
            source="Convention: every class ships a free rank-1 Attack. The "
                   "id matters - combat/abilities.py fires ON_WEAPON_SWING "
                   "only for '<class>_attack', so Crusher keys off this one."),

    # ---- core chassis, all three specs
    ability("ancestral_strike", "Ancestral Strike", "damage",
            "A straight, heavy swing with the whole shoulder behind it.",
            ranks(40, 11, 20), target_type="enemy",
            source="CoA: 'Smash and Ancestral Strike as your Energy fillers'. "
                   "The cheap no-cooldown filler every spec presses, so it "
                   "carries Warrior heroic_strike's curve exactly."),
    ability("whirling_advance", "Whirling Advance", "damage",
            "Cross the ground at a run with the weapon already moving, and "
            "cut whatever is standing in the way.",
            ranks(30, 10, 15, start=10, count=6), cooldown=4,
            target_type="enemy_aoe", max_targets=3,
            source="CoA class tree builds a whole cluster around it - "
                   "Dauntless, Rage Whirling, Forward Advance, Whirling "
                   "Assault - so it is the shared gap-closer. The real one "
                   "dispels a slow on hit; there is no self-dispel hook on a "
                   "damage cast, so Dauntless carries mitigation instead."),
    ability("barbaric_whirl", "Barbaric Whirl", "damage",
            "Spin with both arms out and let the weapon find everything "
            "close enough to matter.",
            ranks(34, 9, 30, start=14, count=7), cooldown=3,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'Barbaric Whirl on any pull of 3+ mobs'. The shared "
                   "cleave. enemy_aoe rather than the is_aoe flag - is_aoe "
                   "is not read by _ability_from_data, so target_type is what "
                   "actually makes an ability hit a pack."),
    ability("unbridled_rage", "Unbridled Rage", "buff",
            "Stop holding anything back. It hurts later and works now.",
            one(12, 20), cooldown=8, duration=3,
            stat_mods={"damage_dealt_pct": 15, "haste": 10},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: 'Unbridled Rage is your main burst window "
                   "(+Physical damage, and it triggers Maximum Carnage's "
                   "whirl)'. The class's signature enrage. This engine has no "
                   "enrage STATE, so the three CoA abilities that only exist "
                   "to keep Smash castable are plain buffs and Smash is "
                   "ungated."),
    ability("defiance", "Defiance", "buff",
            "Decide, briefly and without much evidence, that this is not how "
            "it ends.",
            one(20, 0), cooldown=12, duration=3,
            stat_mods={"damage_taken_pct": -0.3},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: 'Defiance (damage taken cut 30-80% the lower your "
                   "health)'. A buff's stat_mods are read raw by "
                   "take_damage's taken_mult, so damage_taken_pct is a "
                   "FRACTION here. The health-scaled 30-to-80% band has no "
                   "hook on a cast buff, so it lands at the floor, 30%; the "
                   "scaling half is covered by Blood and Glory's "
                   "low_health_damage_reduction_pct in the Brutality tree."),
    ability("jawbreaker", "Jawbreaker", "debuff",
            "One short punch to the jaw. Whatever they were saying stops.",
            one(8, 15), cooldown=5, duration=1,
            stat_mods={}, target_type="enemy", is_stun=True,
            icon=None,
            source="CoA: 'Jawbreaker - interrupting them and preventing any "
                   "spell from that school from being cast for 4 seconds'. "
                   "This engine has ONE crowd-control category, is_stun - "
                   "status_effects.py says so outright ('one mechanic, "
                   "is_stun, with no separate silence/root category') and "
                   "StatusEffectMixin.is_stunned is what actually withholds a "
                   "turn. So the interrupt is is_stun for one turn, which "
                   "this ability already carries. School lockout has no hook. "
                   "DEAD FLAG REMOVED 2026-10-29: stat_mods carried "
                   "{'silenced': 1}, described here as 'the shipped "
                   "convention's tooltip label'. Nothing reads it, and a "
                   "stat_mod shaped exactly like the mechanism it is not IS "
                   "the is_aoe trap - which is why tools/validate_class.py "
                   "now ERRORS on stunned/silenced/rooted/stealthed rather "
                   "than warning. It was removed from the emitted JSON "
                   "earlier the same day and not ported here, so re-running "
                   "this script silently restored it."),
    ability("headhunters_spear", "Headhunter's Spear", "ranged_damage",
            "A light spear, thrown fast and low. You are moving again before "
            "it lands.",
            ranks(44, 13, 20, start=16, count=6), cooldown=4,
            target_type="enemy", generates={"resource": "energy", "amount": 25},
            source="CoA: 'Headhunter's Spear ... restores 30% of your maximum "
                   "Energy'. The `generates` field is how a builder pays in "
                   "one currency and produces another, so the refund is real "
                   "rather than flavour. ranged_damage - it is thrown, and "
                   "Barbarian's weapon map includes thrown/gun/crossbow."),
    ability("maiming_spear", "Maiming Spear", "debuff",
            "Thrown at the legs. They can still come for you, just slowly.",
            one(18, 15), cooldown=5, duration=2,
            stat_mods={"attack_power": -35}, target_type="enemy", icon=None,
            source="CoA: 'Throw your ranged weapon at your enemy's legs ... "
                   "slowing their movement speed by -50%'. There is no "
                   "movement in a turn fight, and a haste debuff would have "
                   "been worse than nothing: a Monster reads ONLY `armor` and "
                   "`attack_power` out of a status effect's stat_mods "
                   "(entities/monster.py), so haste on an enemy is inert. A "
                   "hobbled enemy hitting softer is what actually lands."),
    ability("skull_smash", "Skull Smash", "debuff",
            "Pick up a rock. Throw the rock. They sit down.",
            one(22, 15), cooldown=8, duration=1,
            stat_mods={}, target_type="enemy", is_stun=True,
            icon=None,
            source="CoA: 'hurl it at an enemy's skull, disorienting them ... "
                   "Damage taken will end this effect'. Disorient is modelled "
                   "as the engine's stun, which is the closest honest fit; the "
                   "break-on-damage half has no hook, so the duration is one "
                   "turn to keep it from being strictly better than CoA's. "
                   "DEAD FLAG REMOVED 2026-10-29: stat_mods carried "
                   "{'stunned': 1}, which is read by nothing - the real "
                   "mechanism is the is_stun flag this ability already sets. "
                   "tools/validate_class.py now errors on it. Removed from "
                   "the emitted JSON earlier the same day and not ported "
                   "here, so re-running this script restored it."),
    ability("ancestral_roar", "Ancestral Roar", "heal",
            "You shout something in a language you were never taught, and it "
            "helps.",
            ranks(170, 90, 25, start=26, count=5), cooldown=6,
            target_type="self", icon=None,
            source="CoA: 'Ancestral Roar - Requires Enraged. Roar with "
                   "ancestral fervor, healing you for AP'. Enrage gate "
                   "dropped (no enrage state); the AP scaling is covered by "
                   "the engine's own healing_power contribution rather than a "
                   "literal AP coefficient."),
    ability("warband", "Warband", "hot",
            "You pull the others in close. Nobody in the knot of you bleeds "
            "out quietly.",
            ranks(220, 70, 30, start=30, count=5), cooldown=10, duration=3,
            target_type="party", icon=None,
            source="CoA: 'Bring all nearby allies into the warband for 12 "
                   "seconds, granting them Born in Blood, repeating every 3 "
                   "sec' - and the spec pages are blunt that this 'is a regen "
                   "buff, not triage. It cannot heal a dungeon.' A party HoT "
                   "needs target_type='party'; buff_scope only chooses between "
                   "turn-based and wall-clock duration and would have left "
                   "this self-only."),
    ability("thick_skull", "Thick Skull", "buff",
            "Your skull has been described, more than once, as a structural "
            "feature.",
            one(28, 0), cooldown=12, duration=2,
            stat_mods={"cc_immune": 1}, target_type="self",
            buff_scope="combat", icon=None,
            source="CoA: 'immune to all stun effects for 10 seconds ... "
                   "Usable while stunned'. The usable-while-stunned half has "
                   "no hook. The on-damage Born in Blood grant is carried by "
                   "the Brutality tree's Savagery node instead."),
    ability("hodirs_wrath", "Hodir's Wrath", "spell_damage",
            "The cold that comes out of you is older than you are.",
            ranks(50, 15, 30, start=36, count=4), cooldown=6,
            target_type="enemy_aoe", max_targets=5, damage_school="frost",
            generates={"resource": "energy", "amount": 40}, icon=None,
            source="CoA: 'Erupt with the power of Hodir, dealing AP Frost "
                   "damage to nearby enemies and restoring 100% of your "
                   "maximum Energy'. A full refund would make it free, so the "
                   "generate is 40. spell_damage with damage_school='frost' "
                   "because effect_type='damage' is hardcoded physical - see "
                   "the module docstring on where a non-caster's Frost scaling "
                   "comes from."),

    # ---- Brutality
    ability("smash", "Smash", "damage",
            "Everything you have, into one place, with no plan for the "
            "follow-up.",
            ranks(58, 16, 30, start=18, count=7), target_type="enemy",
            source="CoA: 'Smash, your biggest no-cooldown Energy dump, "
                   "requires an active [enrage]'. No cooldown, so no cooldown "
                   "here either; the enrage requirement is dropped with the "
                   "rest of the enrage state."),
    ability("brutal_swing", "Brutal Swing", "damage",
            "A wide, careless arc. Whoever stood too close to your target "
            "shares in it.",
            ranks(36, 10, 20, start=12, count=7), target_type="enemy_aoe",
            max_targets=3, is_instant=True,
            source="CoA: 'Brutal Swing is your off-global cleave dump between "
                   "specials', 'swing violently at an enemy and up to 2 "
                   "nearby enemies'. off-global = is_instant, the engine's "
                   "turn-based translation of a free action, same as Warrior's "
                   "Cleave."),
    ability("decapitate", "Decapitate", "damage",
            "Finish it. There is no second swing in this one.",
            ranks(100, 28, 30, start=24, count=6), cooldown=3,
            target_type="enemy",
            source="CoA: 'Decapitate to execute once the target is below 35% "
                   "HP (each point of spare Energy adds damage)'. THE GATE IS "
                   "DELIBERATELY ABSENT. execute_threshold_pct exists and is "
                   "PERCENT POINTS (warrior_execute 20, cultist_netherstrike "
                   "35), but its check in Ability.use reads "
                   "`target.current_health / target.health` and Monster has "
                   "no `health` - it uses `max_health`, while only Character "
                   "has `health`. getattr(target, 'health', 0) is therefore 0 "
                   "against every creature in the game, the percentage "
                   "defaults to 100, and the cast is refused. Every "
                   "execute-gated ability shipped today (Warrior's Execute, "
                   "Cultist's Netherstrike, Primalist's Raptor Talons and "
                   "Bring Me Their Bones, Stormbringer's Electrocute) is "
                   "uncastable against a monster for that reason. Authoring "
                   "the gate here would have bought a dead signature ability, "
                   "so Decapitate is an ungated finisher instead - a longer "
                   "cooldown and lower damage than a gated execute would "
                   "carry, since it can be pressed at any health. The "
                   "spend-spare-Energy scaling has no hook either. Worth "
                   "fixing in the engine: one getattr."),
    ability("crush", "Crush", "damage",
            "Bring it down on the front rank. They go down with it.",
            ranks(60, 18, 30, start=22, count=5), cooldown=5,
            target_type="enemy_aoe", max_targets=4, is_stun=True,
            source="CoA: 'Crush is a frontal-cone knockdown and stun', "
                   "'Landing Crush on a full clump as the tank gathers - that "
                   "is the biggest AoE payoff the spec has'."),
    ability("onslaught", "Onslaught", "restore_resource",
            "A second wind you did not earn and will not question.",
            restore(30, 0, 45), cooldown=8,
            target_type="self", restore_resource_type="energy", icon=None,
            source="CoA: 'Onslaught is an Energy battery that floods the bar "
                   "for execute phases'. 45% of the pool, carried on the rank "
                   "key that effect_type='restore_resource' actually reads - "
                   "see restore(). It is also an enrage in CoA; nothing here "
                   "can carry that."),
    ability("battle_vigor", "Battle Vigor", "buff",
            "You get bigger when it is going badly. Nobody has explained it.",
            one(34, 20), cooldown=10, duration=3,
            stat_mods={"max_health_pct": 0.15, "attack_power": 30},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: 'Battle Vigor is a +max-health defensive that still "
                   "counts as an enrage, so it keeps Smash live'. "
                   "max_health_pct is a FRACTION in the shared bonus pool - "
                   "health * (1.0 + value) - not percent points."),
    ability("killing_spree", "Killing Spree", "damage",
            "One is down. You are already looking at the next one.",
            ranks(140, 40, 25, start=40, count=4), cooldown=6,
            target_type="enemy",
            source="CoA: 'Killing Spree to charge back in after a kill blow', "
                   "'Can only be used within 6 seconds of scoring a killing "
                   "blow or applying Born in Blood'. There is no "
                   "recent-kill window to gate a cast on, so it is a plain "
                   "cooldown and the gate is dropped."),
    ability("storm_of_steel", "Storm of Steel", "dot",
            "You stop swinging in single blows and simply do not stop.",
            ranks(100, 28, 35, start=44, count=4), cooldown=6, duration=3,
            target_type="enemy",
            source="CoA: 'Storm of Steel on a tough single target for "
                   "sustained ramp', 'striking your target every 1 sec for 80% "
                   "Weapon Damage for 3 seconds'. A repeating strike over "
                   "three turns is a dot; effect_value is the TOTAL across the "
                   "duration, which is how every shipped dot authors it."),

    # ---- Headhunting
    ability("throw_weapon", "Throw Weapon", "ranged_damage",
            "Whatever is in your hand, at whoever is too far to punch.",
            ranks(34, 9, 15, start=10, count=8), target_type="enemy",
            source="CoA: 'filler Throw Weapon/Berserker Axe'. The spec's "
                   "cheap ranged filler and the hub of its whole kit - Spear "
                   "Thrower resets Spears off it, Gurubashi Technique "
                   "transforms it, Sen'jin's Guidance replaces it."),
    ability("barbed_spear", "Barbed Spear", "ranged_damage",
            "Barbed, so it argues on the way out as well as the way in.",
            ranks(52, 15, 25, start=16, count=6), cooldown=3,
            target_type="enemy",
            source="CoA: 'Barbed Spear to feed Furious Berserker's Born in "
                   "Blood', 'reducing their healing received by -30%'. The "
                   "anti-heal debuff cannot ride along: one cast is one "
                   "effect_type here, and Monster reads only armor and "
                   "attack_power out of a debuff's stat_mods anyway, so "
                   "healing_taken_pct on an enemy would do nothing. Damage "
                   "only, and the crit that feeds Furious Berserker is the "
                   "part the rotation actually asks for."),
    ability("gutspiller", "Gutspiller", "dot",
            "A heavy axe, thrown into the middle of them. It stays there.",
            ranks(84, 24, 25, start=20, count=5), cooldown=4, duration=3,
            target_type="enemy",
            source="CoA: 'Launch a heavy axe at an enemy, causing them to "
                   "bleed for 96 damage over 12 seconds. Every 6 sec the "
                   "target has their Guts Spilled'. The nested Guts Spilled "
                   "tick is folded into the one dot and Payback scales it."),
    ability("berserker_rush", "Berserker Rush", "damage",
            "In at a dead run, and out again before they have straightened "
            "up.",
            ranks(70, 20, 20, start=22, count=5), cooldown=5,
            target_type="enemy",
            source="CoA: 'Berserker Rush's charge-root-then-leap-back', "
                   "'rooting them for 2 seconds, then leap backwards'. Root "
                   "and reposition are both movement, which a turn fight has "
                   "none of. The Born in Blood grant it carries in CoA is the "
                   "Vengeance For Zul'jin talent, which is in the tree."),
    ability("berserker_axe", "Berserker Axe", "ranged_damage",
            "Two axes, one after the other, through whatever they were using "
            "for cover.",
            ranks(48, 14, 20, start=24, count=6), cooldown=2,
            target_type="enemy",
            source="CoA: 'weave Berserker Axe while Enraged', 'Hurl two axes "
                   "at an enemy ... reducing enemy armor by 80'. Enrage gate "
                   "and the 3-charge recharge model both dropped; a short "
                   "cooldown is the engine's version of charges. The armour "
                   "shred is carried by the tree's To The Bone instead, where "
                   "it can be a real debuff."),
    ability("impaling_spear", "Impaling Spear", "dot",
            "Thrown hard enough to go through the first one and keep the "
            "argument going.",
            ranks(96, 26, 30, start=28, count=4), cooldown=5, duration=3,
            target_type="enemy_aoe", max_targets=4,
            source="CoA: 'Impaling Spear is a frontal-line bleed via Spear "
                   "Shards', 'Hurl a spear in a 30 yd frontal line ... At the "
                   "spear's impact location the spear shatters'. The line and "
                   "the shatter collapse into one capped AoE bleed."),
    ability("savage_revelry", "Savage Revelry", "heal",
            "You laugh at something that is not funny and feel better for it.",
            ranks(190, 100, 0, start=26, count=5), cooldown=8,
            target_type="self", generates={"resource": "energy", "amount": 20},
            icon=None,
            source="CoA: \"Savage Revelry's health-and-Energy restore is your "
                   "only quick button\". Both halves are real here - the heal "
                   "through effect_type, the Energy through `generates`."),
    ability("axe_twirling", "Axe Twirling", "buff",
            "You start showing off. It is, annoyingly, also the correct play.",
            one(32, 25), cooldown=10, duration=3,
            stat_mods={"damage_dealt_pct": 20, "crit_chance_physical": 8},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: 'Axe Twirling is your burst button, an Enrage that "
                   "makes Throw Weapon, Gutspiller and Berserker Axe strike "
                   "additional nearby enemies'. A buff cannot retarget another "
                   "ability's cleave, so the window is a damage window; the "
                   "cleave half is already in the kit as Brutal Swing and "
                   "Barbaric Whirl."),
    ability("javelin_toss", "Javelin Toss", "ranged_damage",
            "Taken slowly, aimed properly, thrown once.",
            ranks(120, 34, 30, start=38, count=4), cooldown=3,
            target_type="enemy",
            source="CoA: \"Open at range with Javelin Toss/Throw Weapon\", "
                   "and Sen'jin's Guidance 'Transforms your Throw Weapon into "
                   "Javelin Toss'. A transform has no hook, so it is its own "
                   "later, bigger thrown attack and the talent buffs it."),
    ability("spite", "Spite", "ranged_damage",
            "Three in a row, then you are somewhere else entirely.",
            ranks(150, 40, 35, start=44, count=3), cooldown=8,
            target_type="enemy",
            source="CoA: 'Spite bursts and flings you a long way', 'Quickly "
                   "unleash 3 Berserker Throws at your target and then fling "
                   "yourself back'. Three throws resolve as one hit; the "
                   "reposition is dropped."),

    # ---- Ancestry
    ability("keg_smash", "Keg Smash", "damage",
            "Swing the tankard like it was built for this. It mostly was.",
            ranks(38, 10, 25, start=12, count=8), cooldown=2,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'Keg Smash on cooldown (boosted by Trip to the "
                   "Alehouse) as your core AoE/ST frost+physical hit'. Kept "
                   "physical (effect_type='damage') because it is the one "
                   "ability this spec presses every turn and should not depend "
                   "on the Frozen Warlord conversion to function; the Frost "
                   "half of the kit is Breath of the North and Frozen "
                   "Tankard."),
    ability("ancestral_combat", "Ancestral Combat", "buff",
            "You stop fighting alone without anyone arriving.",
            one(16, 20), cooldown=0, duration=4,
            stat_mods={"haste": 12, "frost_resistance": 15},
            target_type="self", buff_scope="combat", icon=None,
            proc={"trigger": "on_damage_cast", "chance": 25, "icd": 0,
                  "bonus_pct": 0.2},
            source="CoA: \"Keep Ancestral Combat's self-buff rolling: it gives "
                   "a chance for bonus Frost main-hand swings\". The bonus "
                   "swing is a real 25% bonus_pct proc on the buff itself - "
                   "extra damage on the same hit, which is what an extra "
                   "main-hand attack buys. The Fill Level it also generates "
                   "has no pool to go into."),
    ability("ancestral_fury", "Ancestral Fury", "buff",
            "The pace you set is the pace everyone ends up keeping.",
            one(18, 20), duration=0, stat_mods={"haste": 10},
            target_type="party", icon=None,
            source="CoA: 'Ancestral Fury and Frozen Blades stay up passively. "
                   "Position so the whole group sits in your haste and crit "
                   "auras.' An always-on aura, so it keeps the default "
                   "wall-clock buff_scope rather than expiring with the fight."),
    ability("breath_of_the_north", "Breath of the North", "spell_damage",
            "You breathe out and the air in front of you stops being "
            "survivable.",
            ranks(46, 13, 25, start=20, count=5), cooldown=4,
            target_type="enemy_aoe", max_targets=4, damage_school="frost",
            icon=None,
            source="CoA: 'Breath of the North whenever the Tankard is empty', "
                   "'dealing AP Frost damage to enemies in a 12 yd cone'. The "
                   "empty-Tankard gate needs a second resource this class does "
                   "not have, so it is a plain cooldown."),
    ability("frozen_blades", "Frozen Blades", "buff",
            "Everyone's edges come away colder than they went in.",
            one(24, 20), duration=0,
            stat_mods={"crit_chance_physical": 5, "frost_resistance": 10},
            target_type="party", icon=None,
            source="CoA: 'Critical strikes now grant party and raid members 5% "
                   "critical strike chance'. The crit-triggered half is "
                   "flattened into a standing aura, which is how the spec page "
                   "describes playing it anyway ('stay up passively')."),
    ability("frozen_tankard", "Frozen Tankard", "spell_damage",
            "You throw a full one. It is a waste and it works.",
            ranks(60, 17, 20, start=26, count=4), cooldown=6,
            target_type="enemy", damage_school="frost", is_stun=True,
            icon=None,
            source="CoA: 'Frozen Tankard is a thrown Frost stun that flags "
                   "Frozen', 'Open dangerous pulls with Frozen Tankard to "
                   "stun'. The Frozen flag that Icebound Ancestry reads off it "
                   "has no hook, so that node carries flat crit instead."),
    ability("ramhorn_rage", "Ramhorn Rage", "hot",
            "Something with horns is angry on your behalf, and everyone "
            "standing near you benefits.",
            ranks(240, 80, 30, start=28, count=5), cooldown=10, duration=3,
            target_type="party", icon=None,
            source="CoA: 'Ramhorn Rage at the start of a hard pull ... Its "
                   "max-HP regen (extended by your own autoattacks) is the "
                   "closest thing you have to a group heal'. Max-HP-proportional "
                   "ticks and autoattack extension both have no hook, so it is "
                   "a flat party HoT."),
    ability("ancestors_call", "Ancestor's Call", "summon_pet",
            "You say a name you only half remember. Something answers it.",
            one(30, 30), cooldown=0, target_type="self",
            summon_pet_template="honored_ancestor", icon=None,
            source="CoA: 'Call an Honored Ancestor to aid you in battle until "
                   "dismissed that scales with your Agility and attack "
                   "power ... Whenever you use Barbaric Whirl or Whirling "
                   "Advance, your Honored Ancestor mimics it.' NOW A REAL "
                   "HONORED ANCESTOR. This pointed at 'wolf' and summoned a "
                   "pet named Wolf - the old note called a called spirit "
                   "beast 'the closest honest reading', which it was while no "
                   "ancestor template existed. One does now: a spirit warrior "
                   "with high crit to match the Ancestry tree's own One With "
                   "The Ancestors. TWO HALVES STILL UNHOOKED. Scaling off the "
                   "owner's Agility and attack power is impossible by design "
                   "- Pet._apply_template_stats reads exactly three owner "
                   "TALENT keys (pet_damage, pet_health, pet_armor) and "
                   "nothing else, deliberately, so an owner STAT has no "
                   "route; The Spins and Might of Utgarde scale the pet "
                   "through those talent keys instead. The mimic mechanic "
                   "would need a pet to react to its owner's casts, which "
                   "nothing in the pet system does; Spirit Whirl keeps the "
                   "flavour as an ability the Ancestor casts itself."),
    ability("cheers", "Cheers!", "buff",
            "You put a drink in their hand and take the next hit meant for "
            "them.",
            one(36, 15), duration=0,
            stat_mods={"damage_taken_pct": -0.08, "stamina": 6},
            target_type="ally", icon=None,
            source="CoA: \"Cheers! on the squishiest party member, or the "
                   "healer. It redirects part of their incoming damage onto "
                   "yourself and cuts what they take.\" The redirect has no "
                   "hook - nothing reroutes damage between combatants - so "
                   "only the reduction is real, and it is small because of it."),
    ability("war_cry", "War Cry", "buff",
            "A noise that makes the people beside you faster and the people "
            "in front of you slower.",
            one(38, 25), cooldown=12, duration=4,
            stat_mods={"attack_power": 60, "haste": 15},
            target_type="party", buff_scope="combat", icon=None,
            source="CoA: 'War Cry / Splash Zone at pull start for the party's "
                   "attack-speed and attack/spell power burst', 'increasing "
                   "melee and ranged attack speed by 20%, and attack power by "
                   "150 of allies'."),
    ability("splash_zone", "Splash Zone", "buff",
            "You share the tankard around. Generously, and without asking.",
            one(40, 25), cooldown=12, duration=4,
            stat_mods={"attack_power": 45, "spell_power": 45},
            target_type="party", buff_scope="combat", icon=None,
            source="CoA: 'Share a drink from your Tankard with all party and "
                   "raid members, granting 95 increased attack or spell "
                   "power'. CoA's either/or is both here - there is no "
                   "'whichever stat you use' selector, and giving both is "
                   "closer to the intent than guessing."),
    ability("ale_of_the_god_king", "Ale of the God-King", "buff",
            "A drink brewed for someone who never had to ask twice.",
            one(42, 25), cooldown=10, duration=4,
            stat_mods={"spell_power": 50, "frost_resistance": 20},
            target_type="self", buff_scope="combat", icon=None,
            source="CoA: \"Empower your Honored Ancestor's melee attacks to "
                   "deal additional Frost damage scaling with your attack "
                   "power\", 'Ale of the God-King the instant your Tankard is "
                   "full'. NOTHING a cast can carry reaches a pet: "
                   "summon_damage_pct is authored on one shipped ability and "
                   "read nowhere, and pet_damage/pet_health/pet_armor are "
                   "read ONLY off the owner's TALENT effects, once, at Pet "
                   "construction (entities/pet.py). So the Barbarian drinks "
                   "it himself and his own Frost gets heavier - spell_power "
                   "is what Breath of the North, Frozen Tankard and Hodir's "
                   "Wrath read. The pet-facing half lives in the Ancestry "
                   "tree as The Spins and Might of Utgarde, where pet_damage "
                   "and pet_health are real. The Tankard gate is gone with "
                   "the Tankard."),
    ability("tavern_brawl", "Tavern Brawl!", "buff",
            "Someone throws the first punch and it stops being your problem "
            "to start one.",
            one(44, 30), cooldown=15, duration=3,
            stat_mods={"haste": 30}, target_type="party",
            buff_scope="combat", icon=None,
            source="CoA: \"Tavern Brawl! as the group haste cooldown for burn "
                   "phases\", 'Enrage all nearby allies, increasing their "
                   "haste by 30%'. The 5-minute exhaustion lockout has no "
                   "hook; the 15-turn cooldown stands in for it."),
    ability("clanlords_totem", "Clanlord's Totem", "buff",
            "You drive it into the ground and the ground agrees with you.",
            one(46, 30), cooldown=12, duration=4,
            stat_mods={"damage_dealt_pct": 12, "frost_resistance": 25},
            target_type="party", buff_scope="combat", icon=None,
            source="CoA: \"Clanlord's Totem dropped at the fight to buff "
                   "allies standing near it\", 'causing allied players ... to "
                   "deal 35% AP additional damage as Frost'. There is no "
                   "placed-object system and no 'your allies' damage becomes "
                   "Frost' hook, so it is a party damage window. Not "
                   "effect_type='totem_loadout' - that is the Shaman's "
                   "totem-slot swap, a different mechanic entirely."),
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


def born_in_blood(effect_id):
    """CoA's Born in Blood, as a proc payload.

    "Battle fuels your vitality, restoring 18 health and 12 Energy over 3
    seconds." Six separate CoA talents across the class tree and two specs
    grant it, and the spec pages call it the reason this class does not need
    a healer. It is never cast, so it is not an ability here - it is an
    apply_effect HoT plus a grant_resource, the pair of payloads that
    together are what the buff actually does. Each granting talent passes its
    own effect_id so the HoTs refresh per source rather than colliding.
    """
    return ({"effect_id": effect_id, "name": "Born in Blood",
             "effect_type": "hot", "duration": 3, "potency": 30,
             "on_target": False},
            {"resource": "energy", "amount": 12})


# ============================================================== Brutality
B = "barbarian_brutality"
_bib_savagery, _bib_savagery_energy = born_in_blood("barbarian_bib_savagery")
_bib_sustain, _bib_sustain_energy = born_in_blood("barbarian_bib_sustaining")
BRUTALITY = tree(
    B, "Barbarian Brutality",
    "Two-handed builder-spender melee - cheap fillers into Smash, cleave "
    "when the pack clumps, and Decapitate to finish anything under 35%. The "
    "self-healing is in the rotation rather than on a cooldown.",
    [
        node(B, "pure_power", "Pure Power",
             "Increases the damage of Smash by 5% per rank.",
             0, 0, 5, {"ability_barbarian_smash_damage": 0.05},
             source="CoA: 'Pure Power - Increases the damage of Smash by 15% "
                    "and your expertise by 5'. There is no expertise key in "
                    "this engine (dodge/parry are rolled by the defender, with "
                    "no attacker-side offset), so only the damage half lands."),
        node(B, "reckless_movements", "Reckless Movements",
             "Increases the damage of Ancestral Strike and Barbaric Whirl by "
             "4% per rank.",
             0, 1, 5, {"ability_barbarian_ancestral_strike_damage": 0.04,
                       "ability_barbarian_barbaric_whirl_damage": 0.04},
             source="CoA: 'Increases the damage of Ancestral Strike and "
                    "Barbaric Whirl by 20%'. ability_<id>_<stat> keys are "
                    "built by string interpolation in abilities.py, so a "
                    "literal grep calls them dead."),
        node(B, "savage_strength", "Savage Strength",
             "Increases your Agility by 2% per rank.",
             0, 2, 5, {"agility_pct": 2.0},
             source="CoA class tree: 'Savage Strength - Increases your Agility "
                    "by 5%'. Agility is the spec's primary stat per its own "
                    "stat priority."),
        node(B, "excessive_power", "Excessive Power",
             "Increases your maximum Energy by 6 per rank.",
             0, 3, 5, {"energy_max": 6},
             source="CoA: 'Excessive Power raises your max Energy' (its real "
                    "wording is +100%). energy_max is the <resource>_max "
                    "family read by get_resource_max; 30 extra at 5/5 against "
                    "a 100 pool is the shipped scale, not CoA's doubling."),

        node(B, "bloody_fighter", "Bloody Fighter",
             "Increases the critical strike chance of Brutal Swing and Smash "
             "by 2% per rank.",
             1, 0, 5, {"ability_barbarian_brutal_swing_crit": 2.0,
                       "ability_barbarian_smash_crit": 2.0},
             connect=["pure_power"],
             source="CoA: 'Increases the critical strike chance of Brutal "
                    "Swing and Smash by 5%'. ability_<id>_crit is read in "
                    "_roll_crit in percentage points, the same unit as "
                    "crit_chance_physical - a real per-ability crit key, so "
                    "this does not have to become global crit."),
        node(B, "relentless", "Relentless",
             "Your critical strikes with Ancestral Strike and Brutal Swing "
             "have a 30% chance per rank to refund 10 Energy.",
             1, 1, 3, {}, connect=["reckless_movements"],
             proc={"trigger": "on_crit", "chance": 30, "icd": 0,
                   "ability_filter": ["barbarian_ancestral_strike",
                                      "barbarian_brutal_swing"],
                   "grant_resource": {"resource": "energy", "amount": 10}},
             source="CoA: 'Critical strikes with Ancestral Strike and Brutal "
                    "Swing now refund 10 Energy'. _sync_talent_procs scales a "
                    "multi-rank proc's CHANCE by points spent and nothing "
                    "else, so the tooltip has to read 'per rank' on the "
                    "chance."),
        node(B, "efficient_killer", "Efficient Killer",
             "Reduces the Energy cost of your abilities by 2% per rank.",
             1, 2, 3, {"all_ability_cost_pct": 0.02},
             connect=["savage_strength"],
             source="CoA: 'Reduces the Energy cost of your spells and "
                    "abilities by -10%'."),
        node(B, "ogres_strength", "Ogre's Strength",
             "Grants attack power equal to 2% of your Strength per rank.",
             1, 3, 5, {"ap_from_strength_pct": 0.02},
             connect=["excessive_power"],
             source="CoA free passive: 'Increases your attack power by 30% of "
                    "your Strength'. A real <target>_from_<source>_pct "
                    "conversion, resolved against the shared STAT_CONVERSION "
                    "maps in character.py."),

        node(B, "spiked_weapons", "Spiked Weapons",
             "Increases your critical strike damage by 4% per rank.",
             2, 0, 3, {"crit_damage_physical": 0.04},
             connect=["bloody_fighter"],
             source="CoA: 'Increases the critical damage of Crush, Brutal "
                    "Swing, and Decapitate by 20%'. ability_<id>_crit_damage "
                    "exists but only takes one id, and this names three, so "
                    "it lands as the global physical crit-damage key at a "
                    "smaller per-rank value."),
        node(B, "anger_issues", "Anger Issues",
             "Your critical strikes have a 25% chance per rank to knock a "
             "turn off Barbaric Whirl and Crush.",
             2, 1, 3, {}, connect=["relentless"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "reset_cooldown": {"abilities": ["barbarian_barbaric_whirl",
                                                    "barbarian_crush"],
                                      "turns": 1}},
             source="CoA: 'Scoring a critical strike against an enemy now "
                    "reduces the cooldown of Carnage by -4 sec', and the "
                    "playstyle note 'banking crits to shorten Carnage's "
                    "cooldown via Anger Issues'. reset_cooldown with a `turns` "
                    "value is a real proc payload - omitting turns would reset "
                    "outright, which is stronger than CoA's."),
        node(B, "battering_ram", "Battering Ram",
             "Increases your armor penetration by 6 per rank.",
             2, 2, 3, {"armor_penetration": 6},
             connect=["efficient_killer"],
             source="CoA: 'Increases your Armor penetration by 10% while "
                    "wielding a two-handed mace or axe', and the spec's stat "
                    "priority lists Armor Penetration. armor_penetration is "
                    "real and subtracted from the defender's Armor in both "
                    "Character.take_damage and Monster.take_damage; the "
                    "weapon-type condition has no hook, so the value is flat "
                    "and modest (18 at 3/3 against a level 60 humanoid's 118 "
                    "Armor)."),
        node(B, "horde_breaker", "Horde Breaker",
             "Your Crush leaves enemies Wounded, reducing their armor by 35.",
             2, 3, 3, {}, connect=["ogres_strength"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["barbarian_crush"],
                   "apply_effect": {"effect_id": "barbarian_wounded",
                                    "name": "Wounded",
                                    "effect_type": "debuff",
                                    "duration": 3,
                                    "stat_mods": {"armor": -35},
                                    "on_target": True}},
             source="CoA: 'Your Crush ... now applies Wounded to enemies for "
                    "10 seconds. Wounded: Increases Physical Damage taken by "
                    "4%'. A Monster reads only `armor` and `attack_power` out "
                    "of a status effect's stat_mods (entities/monster.py), so "
                    "physical_damage_taken_pct on an enemy debuff would do "
                    "nothing - armour shred is the version that lands. The "
                    "guaranteed-crit-on-Headbutt half has no hook."),

        node(B, "headlopper", "Headlopper",
             "Your critical strikes with Decapitate have a 50% chance per "
             "rank to leave the enemy bleeding.",
             3, 0, 2, {}, connect=["spiked_weapons"],
             proc={"trigger": "on_crit", "chance": 50, "icd": 0,
                   "ability_filter": ["barbarian_decapitate"],
                   "apply_effect": {"effect_id": "barbarian_headlopper",
                                    "name": "Headlopper",
                                    "effect_type": "dot",
                                    "duration": 3, "potency": 45,
                                    "damage_school": "physical",
                                    "on_target": True}},
             source="CoA: 'Your critical strikes with Decapitate now cause the "
                    "enemy to bleed, dealing an additional 30% of the damage "
                    "dealt over 5 seconds'. A proc payload's potency is static, "
                    "so the bleed is a flat tick rather than a share of the "
                    "hit that caused it."),
        node(B, "crusher", "Crusher",
             "Your melee attacks have a 10% chance per rank to reset Crush.",
             3, 1, 3, {}, connect=["anger_issues"],
             proc={"trigger": "on_weapon_swing", "chance": 10, "icd": 0,
                   "reset_cooldown": {"ability": "barbarian_crush"}},
             source="CoA: 'Melee auto attacks now have a 10% chance to reset "
                    "the cooldown of Crush'. ON_WEAPON_SWING fires only for "
                    "'<class>_attack' - a real basic-attack-only trigger, "
                    "which is exactly what 'auto attacks' means."),
        node(B, "whirling_assault", "Whirling Assault",
             "Increases the damage of Whirling Advance by 10% per rank.",
             3, 2, 3, {"ability_barbarian_whirling_advance_damage": 0.10},
             connect=["battering_ram"],
             source="CoA: 'Increases the damage of Whirling Advance by 300% on "
                    "enemies above 80% health'. There is no above-80% "
                    "condition, so it is a flat increase at a fraction of "
                    "CoA's size."),
        node(B, "rancor", "Rancor",
             "Your Brutal Swing has a 25% chance per rank to trigger an "
             "additional attack.",
             3, 3, 3, {}, connect=["horde_breaker"],
             proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
                   "ability_filter": ["barbarian_brutal_swing"],
                   "extra_attack": 1},
             source="CoA: 'Your Brutal Swing now triggers an additional auto "
                    "attack on the primary target'. extra_attack is the real "
                    "Windfury-style payload, re-invoking the basic attack "
                    "through the caster's own ability_book."),

        node(B, "thirst_for_battle", "Thirst for Battle",
             "Your Smash has a 33% chance per rank to return 12 Energy.",
             4, 0, 3, {}, connect=["headlopper"],
             proc={"trigger": "on_damage_cast", "chance": 33, "icd": 0,
                   "ability_filter": ["barbarian_smash"],
                   "grant_resource": {"resource": "energy", "amount": 12}},
             source="CoA: 'Your Smash now regenerate 25% of your maximum "
                    "Energy', and 'Smash being near-free thanks to Thirst for "
                    "Battle's Energy refund'. A guaranteed 25-Energy refund on "
                    "a 30-cost ability would make the spec's main dump free, "
                    "so it is a chance at a smaller amount."),
        node(B, "sustaining_swings", "Sustaining Swings",
             "Your attacks have a 3% chance per rank to heal you for 10% of "
             "the damage dealt.",
             4, 1, 3, {}, connect=["crusher"],
             proc={"trigger": "on_damage_cast", "chance": 3, "icd": 0,
                   "leech_pct": {"pct": 0.1}},
             source="CoA: 'Melee attacks now have an 8% chance to heal you for "
                    "10% of the damage dealt'. leech_pct heals off the "
                    "triggering amount, which is exactly this. The 'next "
                    "Ancestral Strike deals 50% more' half has no hook."),
        node(B, "overkill", "Overkill",
             "Increases the critical strike chance of Decapitate by 4% per "
             "rank.",
             4, 2, 3, {"ability_barbarian_decapitate_crit": 4.0},
             connect=["whirling_assault"],
             source="CoA: 'Increases the critical strike chance of Decapitate "
                    "and Headhunter's Spear by 30% against targets below 20% "
                    "health'. Decapitate already requires a target below 35%, "
                    "so the condition is most of the way there; the "
                    "below-20% part is not expressible."),

        node(B, "body_builder", "Body Builder",
             "Grants attack power equal to 3% of your Agility per rank.",
             5, 0, 2, {"ap_from_agility_pct": 0.03},
             connect=["thirst_for_battle"], total_slots=3,
             source="CoA free passive: 'You now gain 1 Strength for every 3 "
                    "Agility'. strength is not a valid conversion TARGET - "
                    "STAT_CONVERSION_TARGETS in character.py accepts attack "
                    "power, spell power, healing power, armor, block value, "
                    "parry, dodge, haste and crit, not the core stats - so the "
                    "conversion goes straight to what Strength was for here."),
        node(B, "blood_and_glory", "Blood and Glory",
             "While below 35% health, you take 8% less damage and your "
             "healing received is 3% stronger, per rank.",
             5, 1, 2, {"low_health_damage_reduction_pct": 0.08,
                       "low_health_threshold_pct": 0.35,
                       "low_health_healing_pct": 0.03},
             connect=["sustaining_swings"], total_slots=3,
             source="CoA class tree: 'While at or below 35% maximum health, "
                    "you now gain 20% increased healing received and take "
                    "-10% reduced damage'. Both halves are real keys and the "
                    "35% threshold is CoA's own number."),
        node(B, "steelslinger", "Steelslinger",
             "Increases the damage your abilities deal to additional targets "
             "by 8% per rank.",
             5, 2, 2, {"aoe_damage": 0.08},
             connect=["overkill"], total_slots=3,
             source="CoA: 'Reduces the cooldown of Barbaric Whirl by -2 sec "
                    "and increases its damage dealt by 100% on enemies below "
                    "35% health'. aoe_damage is read for any enemy_aoe cast, "
                    "which covers Barbaric Whirl, Brutal Swing and Crush "
                    "together - the spec is 'an AoE/cleave specialist' per the "
                    "reference, so the shared key is the right home."),

        node(B, "maximum_carnage", "Maximum Carnage",
             "You stop choosing targets and simply keep the weapon moving.",
             6, 0, 1, {"physical_damage": 0.12, "aoe_damage": 0.15},
             node_type="active",
             connect=["body_builder", "blood_and_glory", "steelslinger"],
             total_slots=1,
             source="Capstone. CoA: 'Casting Unbridled Rage now causes you to "
                    "begin swinging your weapon around you dealing AP Physical "
                    "damage to up to 5 nearby enemies over 5 seconds', and it "
                    "is the thing the whole rotation is built to light up "
                    "('Open with Unbridled Rage on anything more than a single "
                    "mob to trigger Maximum Carnage's whirl'). A talent cannot "
                    "add a persistent whirl to another ability's cast, so the "
                    "payoff is the damage that whirl was worth."),
    ],
    "Built from reference/coa_sidekick/SPEC_barbarian__brutality.txt and the "
    "brutality block of reference/coa_sidekick/talents/barbarian.json. CoA "
    "calls this 'the closest to retail Fury Warrior, but with "
    "Second-Wind-style self-healing built into the rotation instead of bolted "
    "on' and rates it the class's leveling spec. Its stat priority is Hit > "
    "Expertise > Agility > Crit > Armor Penetration > Haste, which is why the "
    "tree spends on crit, crit damage and armour penetration rather than on "
    "raw attack power. Two CoA mechanics shaped what is here and what is not: "
    "the Enrage engine (three enrage abilities existing to keep Smash "
    "castable) has no state to hang on, so Smash is ungated and the enrages "
    "are ordinary buffs; and the self-sustain is deliberately kept as PROCS "
    "(Sustaining Swings' leech, Blood and Glory's low-health band) rather "
    "than a heal button, because the reference is explicit that this spec has "
    "no quick self-heal.")


# ============================================================ Headhunting
H = "barbarian_headhunting"
_bib_furious, _bib_furious_energy = born_in_blood("barbarian_bib_furious")
_bib_vengeance, _bib_vengeance_energy = born_in_blood("barbarian_bib_vengeance")
HEADHUNTING = tree(
    H, "Barbarian Headhunting",
    "Thrown weapons and bleeds - you pick the range, the damage keeps "
    "ticking while both of you move, and your own critical strikes are what "
    "keep you alive.",
    [
        node(H, "strong_arm", "Strong Arm",
             "Increases the damage of Barbed Spear and Javelin Toss by 3% and "
             "your hit rating by 1 per rank.",
             0, 0, 5, {"ability_barbarian_barbed_spear_damage": 0.03,
                       "ability_barbarian_javelin_toss_damage": 0.03,
                       "hit_rating": 1},
             source="CoA: 'Increases the damage of Spears by 15% and your hit "
                    "chance by 3%'. 'Spears' is an ability FAMILY in CoA and "
                    "this engine only has per-ability keys, so the two the "
                    "rotation actually leans on are named. Hit leads the "
                    "spec's own stat priority."),
        node(H, "puncture_wounds", "Puncture Wounds",
             "Your critical strikes with a thrown spear have a 20% chance per "
             "rank to leave the enemy bleeding.",
             0, 1, 5, {}, proc={"trigger": "on_crit", "chance": 20, "icd": 0,
                                "ability_filter": ["barbarian_barbed_spear",
                                                   "barbarian_javelin_toss",
                                                   "barbarian_headhunters_spear",
                                                   "barbarian_impaling_spear"],
                                "apply_effect": {
                                    "effect_id": "barbarian_puncture_wounds",
                                    "name": "Puncture Wounds",
                                    "effect_type": "dot",
                                    "duration": 3, "potency": 34,
                                    "damage_school": "physical",
                                    "on_target": True}},
             source="CoA: 'Critical strikes with Spears now causes enemies to "
                    "bleed for ranged AP over 6 seconds', and the rotation "
                    "leads with 'maintain Puncture Wounds uptime (Spear "
                    "crits)'. The spec's signature, so it sits at the top of "
                    "the tree at 100% chance when maxed."),
        node(H, "gruesome", "Gruesome",
             "Increases the damage of Throw Weapon and Gutspiller by 3% per "
             "rank.",
             0, 2, 5, {"ability_barbarian_throw_weapon_damage": 0.03,
                       "ability_barbarian_gutspiller_damage": 0.03},
             source="CoA: 'Increases the damage of Throw Weapon, Gutspiller, "
                    "and Guts Spilled by 10%'. Guts Spilled is Gutspiller's "
                    "own nested tick, folded into the one dot here."),
        node(H, "guts_splatter", "Guts Splatter",
             "Your attacks ignore 2% of the enemy's armor per rank.",
             0, 3, 5, {"armor_penetration_pct": 2.0},
             source="CoA: 'Your Gutspiller now allows your abilities to ignore "
                    "10% of the enemy's Armor'. armor_penetration_pct is "
                    "divided by 100 in _recalculate_derived_stats, so 2.0 is "
                    "two percentage points and 5/5 reaches CoA's own 10%. "
                    "Applied to all attacks rather than gated behind "
                    "Gutspiller being up - there is no debuff-present "
                    "condition on an attacker-side stat."),

        node(H, "frothing_savage", "Frothing Savage",
             "Increases the critical strike chance of Barbed Spear and "
             "Berserker Axe by 2% per rank.",
             1, 0, 5, {"ability_barbarian_barbed_spear_crit": 2.0,
                       "ability_barbarian_berserker_axe_crit": 2.0},
             connect=["strong_arm"],
             source="CoA: 'Increases the critical strike chance of Spears and "
                    "Berserker Axe by 8% against bleeding targets'. The "
                    "against-bleeding condition is not expressible; in "
                    "practice Puncture Wounds means it is almost always true."),
        node(H, "entrails", "Entrails",
             "Increases your Agility by 2% per rank.",
             1, 1, 5, {"agility_pct": 2.0}, connect=["puncture_wounds"],
             source="CoA: 'Damage dealt by bleed effects now increases your "
                    "Agility by 1% for 8 seconds, stacking 10 times'. A "
                    "stacking bleed-driven buff has no hook, so the Agility "
                    "is permanent and smaller."),
        node(H, "to_the_bone", "To The Bone",
             "Your Gutspiller Breaks the enemy's defenses, reducing their "
             "armor by 30.",
             1, 2, 3, {}, connect=["gruesome"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["barbarian_gutspiller"],
                   "apply_effect": {"effect_id": "barbarian_break",
                                    "name": "Break",
                                    "effect_type": "debuff",
                                    "duration": 3,
                                    "stat_mods": {"armor": -30},
                                    "on_target": True}},
             source="CoA: 'it now applies Break to the target ... Break: Break "
                    "an enemy's defenses, reducing their armor by -4% for 20 "
                    "seconds, stacking 5 times'. Flat rather than percentage "
                    "and unstacked - max_stacks on a proc payload would make "
                    "one talent point worth -150 Armor against a level 60 "
                    "enemy's 118. This is also where Berserker Axe's own "
                    "armour shred ended up, since a damage cast cannot carry a "
                    "debuff too."),
        node(H, "savage", "Savage",
             "Increases all damage you deal by 2% per rank.",
             1, 3, 3, {"all_damage": 0.02}, connect=["guts_splatter"],
             source="CoA free passive: 'Born in Blood now also increases your "
                    "damage dealt by 5% and its duration is increased by 3 "
                    "sec'. Neither half can key off a proc-applied HoT being "
                    "active, so it is a flat damage increase."),

        node(H, "spear_thrower", "Spear Thrower",
             "Your Throw Weapon has a 10% chance per rank to reset Barbed "
             "Spear and Javelin Toss.",
             2, 0, 3, {}, connect=["frothing_savage"],
             proc={"trigger": "on_damage_cast", "chance": 10, "icd": 0,
                   "ability_filter": ["barbarian_throw_weapon"],
                   "reset_cooldown": {"abilities": ["barbarian_barbed_spear",
                                                    "barbarian_javelin_toss"]}},
             source="CoA free passive: 'Casting Throw Weapon now has a 30% "
                    "chance to reset the cooldown of your Spears', and the "
                    "playstyle note 'Spear Thrower and You Want Axe? let Throw "
                    "Weapon reset your Spears ... so damage ramps the longer "
                    "you stay on a target'."),
        node(H, "legacy_of_the_amani", "Legacy of the Amani",
             "Your thrown spears have an 8% chance per rank to send a second "
             "one after them.",
             2, 1, 3, {}, connect=["entrails"],
             proc={"trigger": "on_damage_cast", "chance": 8, "icd": 1,
                   "ability_filter": ["barbarian_barbed_spear",
                                      "barbarian_javelin_toss",
                                      "barbarian_headhunters_spear"],
                   "cast_ability": "barbarian_throw_weapon"},
             source="CoA: 'Damage dealt by your Spears now has a 25% chance to "
                    "cause you to quickly throw an additional spear that "
                    "strikes for 40% of the damage dealt'. cast_ability fires "
                    "a real free cast; the extra throw is Throw Weapon rather "
                    "than a 40%-scaled copy, which is the closest the payload "
                    "gets."),
        node(H, "furious_berserker", "Furious Berserker",
             "Your critical strikes with Barbed Spear have a 33% chance per "
             "rank to grant Born in Blood.",
             2, 2, 3, {}, connect=["to_the_bone"],
             proc={"trigger": "on_crit", "chance": 33, "icd": 1,
                   "ability_filter": ["barbarian_barbed_spear"],
                   "apply_effect": _bib_furious,
                   "grant_resource": _bib_furious_energy},
             source="CoA: 'Critical strikes with Barbed Spear now grants Born "
                    "in Blood', and the strengths list calls this one of the "
                    "two reasons 'you rarely need a healer'. See "
                    "born_in_blood() for how the buff is modelled."),
        node(H, "no_survivors", "No Survivors",
             "Increases the duration of your bleeds by 8% per rank.",
             2, 3, 3, {"dot_duration_pct": 0.08}, connect=["savage"],
             source="CoA: 'Increases the duration of Axe Twirling, Maiming "
                    "Spear, and Barbed Spear by 5 sec'. Only the bleed half "
                    "has a general key; Axe Twirling's own duration is covered "
                    "by Time To Kill!'s cooldown reduction instead."),

        node(H, "time_to_kill", "Time To Kill!",
             "Reduces the cooldown of Axe Twirling by 1 turn per rank.",
             3, 0, 2, {"ability_barbarian_axe_twirling_cooldown": 1},
             connect=["spear_thrower"],
             source="CoA: 'Reduces the cooldown of Axe Twirling by -15 sec'. "
                    "ability_<id>_cooldown is a flat turn reduction."),
        node(H, "hunting_for_sport", "Hunting for Sport",
             "Increases your armor penetration by 6 per rank.",
             3, 1, 3, {"armor_penetration": 6},
             connect=["legacy_of_the_amani"],
             source="CoA: 'While Unbridled Rage is active, your attacks now "
                    "ignore 20% of the target's Armor', and the spec's own "
                    "weakness list says 'Armor ignore only happens inside "
                    "windows ... your penetration comes and goes with rotation "
                    "state'. There is no buff-present condition on an "
                    "attacker-side stat, so it is always on and smaller."),
        node(H, "vengeance_for_zuljin", "Vengeance For Zul'jin",
             "Your Berserker Rush has a 34% chance per rank to grant Born in "
             "Blood.",
             3, 2, 3, {}, connect=["furious_berserker"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 1,
                   "ability_filter": ["barbarian_berserker_rush"],
                   "apply_effect": _bib_vengeance,
                   "grant_resource": _bib_vengeance_energy},
             source="CoA: 'Casting Berserker Rush now grants you Born in "
                    "Blood'. CoA's is guaranteed; a guaranteed HoT plus 12 "
                    "Energy every 5 turns on top of Furious Berserker's would "
                    "make the spec's sustain unconditional, which the "
                    "reference specifically says it is not."),
        node(H, "raging_spirit", "Raging Spirit",
             "Your Unbridled Rage has a 34% chance per rank to grant 30 "
             "Energy.",
             3, 3, 3, {}, connect=["no_survivors"],
             proc={"trigger": "on_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["barbarian_unbridled_rage"],
                   "grant_resource": {"resource": "energy", "amount": 30}},
             source="CoA: 'Casting Unbridled Rage now grants you 30 Energy', "
                    "and the dungeon note 'Unbridled Rage (via Raging Spirit) "
                    "bridges an Energy gap'. ON_CAST rather than "
                    "ON_DAMAGE_CAST because Unbridled Rage deals no damage, so "
                    "there would be no damage event to hang on."),

        node(H, "payback", "Payback",
             "Increases the damage of Gutspiller by 12% per rank.",
             4, 0, 3, {"ability_barbarian_gutspiller_damage": 0.12},
             connect=["time_to_kill"],
             source="CoA: 'Increases the damage dealt by your Guts Spilled by "
                    "75%'. Guts Spilled is the second half of Gutspiller's own "
                    "bleed here, so the key is Gutspiller's."),
        node(H, "skullseeker", "Skullseeker",
             "Increases your critical strike chance by 1% per rank.",
             4, 1, 3, {"crit_chance_physical": 1.0},
             connect=["hunting_for_sport"],
             source="CoA: 'Increases your critical strike chance against "
                    "enemies above 80% health by 25%'. The above-80% condition "
                    "is not expressible, so it is flat crit at the shipped "
                    "per-rank scale."),
        node(H, "spear_shards", "Spear Shards",
             "Increases the damage of Impaling Spear by 10% per rank.",
             4, 2, 3, {"ability_barbarian_impaling_spear_damage": 0.10},
             connect=["vengeance_for_zuljin"],
             source="CoA: 'Whenever you shatter your Impaling Spear, affected "
                    "enemies bleed for 100% of the damage dealt over 3 "
                    "seconds'. Impaling Spear is already authored as the bleed, "
                    "shatter included, so the shards scale it."),

        node(H, "brutal_form", "Brutal Form",
             "Grants healing power equal to 2% of your Agility per rank.",
             5, 0, 2, {"healing_power_from_agility_pct": 0.02},
             connect=["payback"], total_slots=3,
             source="CoA: 'Increases the tick rate of Born in Blood by -25%, "
                    "allows its healing to scale with your Agility, and it can "
                    "now critically heal you'. The Agility scaling is a real "
                    "<target>_from_<source>_pct conversion and the whole point "
                    "of the node; the tick rate and critical healing are not "
                    "expressible. NOTE this scales the spec's cast heals "
                    "(Savage Revelry, Ancestral Roar), not the proc-applied "
                    "Born in Blood HoT - a HoT tick calls heal(tick_potency()) "
                    "directly and never passes through healing_power."),
        node(H, "gurubashi_technique", "Gurubashi Technique",
             "Your Throw Weapon has a 12% chance per rank to hit for 30% "
             "more.",
             5, 1, 2, {}, connect=["skullseeker"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 12, "icd": 0,
                   "ability_filter": ["barbarian_throw_weapon"],
                   "bonus_pct": 0.3},
             source="CoA: 'Casting Throw Weapon now has a 25% chance to "
                    "transform your next cast of it ... into Rapid Throw. "
                    "Rapid Throw: Throw your ranged weapon 3 times in quick "
                    "succession'. Nothing transforms a queued cast, so the "
                    "payoff lands as bonus damage on the same hit - bonus_pct "
                    "is the engine's instant-proc payload."),
        node(H, "senjins_guidance", "Sen'jin's Guidance",
             "Increases the damage of Javelin Toss by 12% and its critical "
             "strike chance by 3% per rank.",
             5, 2, 2, {"ability_barbarian_javelin_toss_damage": 0.12,
                       "ability_barbarian_javelin_toss_crit": 3.0},
             connect=["spear_shards"], total_slots=3,
             source="CoA: 'Transforms your Throw Weapon into Javelin Toss and "
                    "increases the critical strike chance of Javelin Toss by "
                    "5%'. Javelin Toss is its own ability here rather than a "
                    "transform (see the ability's own note), so the node is "
                    "the half that was always a number."),

        node(H, "berserker", "Berserker",
             "Somewhere in the middle of it you stop aiming and start simply "
             "hitting.",
             6, 0, 1, {"physical_damage": 0.10, "crit_chance_physical": 4.0},
             node_type="active",
             connect=["brutal_form", "gurubashi_technique", "senjins_guidance"],
             total_slots=1,
             source="Capstone. CoA: 'While enraged, your ranged critical "
                    "strikes now grant you Berserker ... Your ranged abilities "
                    "have a 20% chance to unleash Berserker Throw ... While "
                    "active, every offensive ranged ability used increases its "
                    "chance to trigger by 2%'. A ramping self-stacking proc has "
                    "no shape here, so the capstone is the throughput that ramp "
                    "was worth."),
    ],
    "Built from reference/coa_sidekick/SPEC_barbarian__headhunting.txt and the "
    "headhunting block of reference/coa_sidekick/talents/barbarian.json. CoA "
    "calls it 'the closest to retail Survival Hunter with a Feral Druid's "
    "survivability bolted on' and rates it the class's best PvP spec (Arena A, "
    "BG A) on the strength of 'Nobody has to peel for you'. Two things decided "
    "the tree's shape. First, its sustain is entirely self-generated off its "
    "own crits, so Puncture Wounds, Furious Berserker and Vengeance For "
    "Zul'jin are PROCS with real payloads rather than passive stats - that is "
    "the spec. Second, CoA's 'Spears' is an ability family and this engine has "
    "only per-ability keys, so every family-wide talent names the two or three "
    "spears the rotation actually presses instead.")


# ============================================================== Ancestry
A = "barbarian_ancestry"
ANCESTRY = tree(
    A, "Barbarian Ancestry",
    "A Frost and physical brawler who improves everyone standing nearby just "
    "by being there - standing auras, a summoned ancestor, and a party haste "
    "cooldown on top of a real melee rotation.",
    [
        node(A, "trip_to_the_alehouse", "Trip to the Alehouse",
             "Increases the damage of Keg Smash by 4% per rank.",
             0, 0, 5, {"ability_barbarian_keg_smash_damage": 0.04},
             source="CoA: 'Increases the damage of Keg Smash by 10% and its "
                    "range by 3 yds', and the rotation's step 2 is 'Keg Smash "
                    "on cooldown (boosted by Trip to the Alehouse)'. Range is "
                    "not a concept in a turn fight."),
        node(A, "drinking_frenzy", "Drinking Frenzy",
             "Increases your hit rating by 1 per rank.",
             0, 1, 5, {"hit_rating": 1},
             source="CoA: 'Your melee attacks now have a 15% chance to grant a "
                    "stack of Fill Level. In addition, your chance to hit is "
                    "increased by 5%'. Hit leads this spec's stat priority; "
                    "Fill Level has no pool to fill."),
        node(A, "fill_level", "Fill Level",
             "Increases your maximum Energy by 6 per rank.",
             0, 2, 5, {"energy_max": 6},
             source="CoA free passive: 'Grants you Fill Level and the ability "
                    "to manipulate a Tankard. You have a magical Tankard that "
                    "fills up over time ... Some of your other abilities empty "
                    "your Tankard to trigger with a reduced cooldown.' "
                    "CLASS_RESOURCE_MAP gives Barbarian (ENERGY, None) - no "
                    "secondary pool - so the Tankard is gone and the node "
                    "widens the pool it does have. Every Tankard GATE in the "
                    "kit (Breath of the North needs empty, Ale of the God-King "
                    "needs full) is dropped with it."),
        node(A, "frozen_warlord", "Frozen Warlord",
             "Grants spell power equal to 2% of your attack power per rank.",
             0, 3, 5, {"spell_power_from_ap_pct": 0.02},
             source="CoA class tree names Frozen Warlord and Hodir's Wrath as "
                    "the Frost half of a class with 'no magic of their own', "
                    "and Ale of the God-King and Clanlord's Totem both say "
                    "their Frost damage scales 'with your attack power'. This "
                    "is the node that makes that literally true: a real "
                    "<target>_from_<source>_pct conversion, and the reason "
                    "Breath of the North, Frozen Tankard and Hodir's Wrath "
                    "scale at all - spell_damage reads "
                    "get_effective_spell_power, which is otherwise zero on a "
                    "leather Agility melee. Take it first. The freeze-in-place "
                    "half of CoA's wording has no hook."),

        node(A, "improved_ancestral_combat", "Improved Ancestral Combat",
             "Reduces the Energy cost of Ancestral Combat by 2 per rank.",
             1, 0, 5, {"ability_barbarian_ancestral_combat_cost": 2},
             connect=["trip_to_the_alehouse"],
             source="CoA: 'Reduces the Energy cost of your Ancestral Combat by "
                    "-10 and allows it to trigger 3 additional times'. "
                    "ability_<id>_cost is a flat reduction, so 5/5 reaches "
                    "CoA's own -10. The trigger count is the buff's duration "
                    "here and is not separately scalable."),
        node(A, "ice_cold_bubbles", "Ice Cold Bubbles",
             "Increases your Frost damage by 3% per rank.",
             1, 1, 5, {"frost_damage_pct": 0.03},
             connect=["drinking_frenzy"],
             source="CoA: 'Each Fill Level stack now also increases Frost "
                    "damage dealt by 2%'. <school>_damage_pct is assembled at "
                    "runtime in _school_damage_bonus and resolved against the "
                    "school the cast actually deals, so this only touches the "
                    "spec's Frost abilities - which is the point."),
        node(A, "thanes_guard", "Thane's Guard",
             "Increases your Armor by 3% per rank.",
             1, 2, 3, {"armor_pct": 3.0}, connect=["fill_level"],
             source="CoA: 'Gain the Shield proficiency and while wearing a "
                    "shield you gain 40% increased attack speed and 100% "
                    "increased Armor contribution from your shield'. "
                    "Proficiency lives in data/items/weapon_types.json, which "
                    "is shared data this script does not touch, and Barbarian "
                    "has no shield there - so the node keeps the armour it was "
                    "for. armor_pct is PERCENT POINTS (divided by 100 in "
                    "_recalculate_derived_stats), unlike max_health_pct."),
        node(A, "liquid_courage", "Liquid Courage",
             "Reduces all damage you take by 2% per rank.",
             1, 3, 3, {"damage_taken_pct": -0.02},
             connect=["frozen_warlord"],
             source="CoA: 'Each Fill Level stack now reduces your damage taken "
                    "by -2%', and the strengths list pairs it with Ramhorn "
                    "Rage as the reason 'No healer required'. Flat rather than "
                    "per-stack, since the stacks are gone with the Tankard. As "
                    "a TALENT effect damage_taken_pct is a fraction."),

        node(A, "cold_brew", "Cold Brew",
             "Your critical strikes have a 33% chance per rank to return 10 "
             "Energy.",
             2, 0, 3, {}, connect=["improved_ancestral_combat"],
             proc={"trigger": "on_crit", "chance": 33, "icd": 1,
                   "grant_resource": {"resource": "energy", "amount": 10}},
             source="CoA: 'Critical strikes with Frost damage now generate a "
                    "stack of Fill Level. Can only occur once per sec.' A Fill "
                    "Level stack is gone, so the proc hands back the resource "
                    "the spec actually spends. The once-per-second limit is "
                    "icd 1. Not restricted to Frost crits - ability_filter "
                    "names abilities, not schools."),
        node(A, "blind_stupor", "Blind Stupor",
             "Your Keg Smash leaves enemies reeling, reducing their attack "
             "power by 25.",
             2, 1, 3, {}, connect=["ice_cold_bubbles"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["barbarian_keg_smash"],
                   "apply_effect": {"effect_id": "barbarian_blind_stupor",
                                    "name": "Blind Stupor",
                                    "effect_type": "debuff",
                                    "duration": 3,
                                    "stat_mods": {"attack_power": -25},
                                    "on_target": True}},
             source="CoA: 'Damage dealt by Keg Smash now reduces enemies' "
                    "casting speed by -30%'. There is no cast-speed stat on a "
                    "Monster - it reads only armor and attack_power out of a "
                    "status effect - so the stupor takes the swing out of them "
                    "instead, which is the closest thing to it that lands."),
        node(A, "unified_rage", "Unified Rage",
             "Your Unbridled Rage lasts 1 turn longer per rank.",
             2, 2, 2, {"ability_barbarian_unbridled_rage_duration": 1},
             connect=["thanes_guard"],
             source="CoA: 'Your Unbridled Rage now increases your chance to "
                    "trigger Ancestral Combat by 25%'. A talent cannot raise "
                    "another talent-free buff's proc chance, so the node buys "
                    "uptime on the window instead. The sibling CoA class "
                    "talent Unstoppable Rage ('+2 sec duration of Unbridled "
                    "Rage') is the same effect, so the name it carries is "
                    "real."),
        node(A, "hodirs_revenge", "Hodir's Revenge",
             "Your Frozen Tankard leaves enemies exposed, reducing their "
             "armor by 40.",
             2, 3, 3, {}, connect=["liquid_courage"],
             proc={"trigger": "on_damage_cast", "chance": 34, "icd": 0,
                   "ability_filter": ["barbarian_frozen_tankard"],
                   "apply_effect": {"effect_id": "barbarian_hodirs_revenge",
                                    "name": "Hodir's Revenge",
                                    "effect_type": "debuff",
                                    "duration": 3,
                                    "stat_mods": {"armor": -40},
                                    "on_target": True}},
             source="CoA: 'Enemies damaged by your Frozen Tankard now take 50% "
                    "increased damage from you for 6 seconds'. A "
                    "damage-taken-increase debuff does nothing to a Monster "
                    "(see Horde Breaker), so it lands as armour shred - and "
                    "Frozen Tankard opens the pull, which is when a shred is "
                    "worth most."),

        node(A, "icebound_ancestry", "Icebound Ancestry",
             "Increases the critical strike chance of Breath of the North by "
             "3% per rank.",
             3, 0, 3, {"ability_barbarian_breath_of_the_north_crit": 3.0},
             connect=["cold_brew"],
             source="CoA: 'Increases the critical strike chance of Breath of "
                    "the North by 10%. In addition, your attacks now ignore "
                    "Armor against Frozen targets.' The Frozen flag Frozen "
                    "Tankard sets has no hook, so only the crit half lands - "
                    "and that half is a real per-ability crit key."),
        node(A, "frost_giants_fury", "Frost Giant's Fury",
             "Increases your haste by 1 per rank.",
             3, 1, 3, {"haste": 1.0}, connect=["blind_stupor"],
             source="CoA: 'Casting Breath of the North now grants you 10% "
                    "melee attack speed, plus an additional 20% when using a "
                    "two-handed weapon, for 8 seconds'. A talent cannot attach "
                    "a buff to another ability's cast, and there is no "
                    "weapon-type condition, so it is flat haste at the shipped "
                    "per-rank scale. Haste is this spec's second stat "
                    "priority."),
        node(A, "the_spins", "The Spins",
             "Increases your ancestor's damage by 6% per rank.",
             3, 2, 3, {"pet_damage": 0.06}, connect=["unified_rage"],
             source="CoA: 'Casting Keg Smash now causes your Honored Ancestor "
                    "to perform an Ancestral Whirl attack upon nearby "
                    "enemies'. Nothing makes a pet mirror the owner's cast, so "
                    "the extra attacks become the damage they were worth. "
                    "pet_damage is read in entities/pet.py."),
        node(A, "breaking_morale", "Breaking Morale",
             "Reduces the Energy cost of your abilities by 2% per rank.",
             3, 3, 3, {"all_ability_cost_pct": 0.02},
             connect=["hodirs_revenge"],
             source="CoA: 'Reduces the Energy cost of Break by -15'. Break is "
                    "the To The Bone debuff from the Headhunting tree, which "
                    "is not an ability here, so the reduction goes to the pool "
                    "it was always paying from."),

        node(A, "might_of_utgarde", "Might of Utgarde",
             "Increases your ancestor's health by 6% per rank.",
             4, 0, 3, {"pet_health": 0.06}, connect=["icebound_ancestry"],
             source="CoA: 'Attacks from your Ancestral Combat now heal your "
                    "Honored Ancestor for 5% maximum health and cause it to "
                    "perform an Ancestral Whirl attack'. There is no pet-heal "
                    "proc, so the node keeps the ancestor alive the other way."),
        node(A, "frozen_blades", "Frozen Blades",
             "Increases your critical strike chance by 1% per rank.",
             4, 1, 3, {"crit_chance_physical": 1.0},
             connect=["frost_giants_fury"],
             source="CoA: 'Critical strikes now grant party and raid members "
                    "5% critical strike chance for 8 seconds'. A talent effect "
                    "only ever applies to its owner - get_talent_effects feeds "
                    "the owner's bonus pool and nothing else - so the "
                    "party-facing half is the cast ability of the same name and "
                    "this node is the Barbarian's own share."),
        node(A, "ancestors_fury", "Ancestor's Fury",
             "Increases your Frost critical strike damage by 4% per rank.",
             4, 2, 3, {"frost_crit_damage_pct": 0.04},
             connect=["the_spins"],
             source="CoA: 'Unbridled Rage now also increases your Frost damage "
                    "by 10%'. The during-Unbridled-Rage condition is not "
                    "expressible; the burst flavour survives as crit damage "
                    "rather than a second flat Frost increase on top of Ice "
                    "Cold Bubbles. <school>_crit_damage_pct is resolved per "
                    "cast in _crit_damage_bonus."),

        node(A, "rage_of_the_north", "Rage of the North",
             "Increases your Frost spell power by 8 per rank.",
             5, 0, 2, {"frost_spell_power": 8},
             connect=["might_of_utgarde"], total_slots=3,
             source="CoA: 'Increases the amount of attacks that can trigger "
                    "your Ale of The God-King by 10'. No hook for that, so the "
                    "node does the other thing the spec's late tier wants: "
                    "more Frost behind every cast. Stacks additively with "
                    "Frozen Warlord's conversion in "
                    "get_effective_spell_power."),
        node(A, "uniting_voice", "Uniting Voice",
             "Increases your haste by 1 and your healing done by 3% per rank.",
             5, 1, 2, {"haste": 1.0, "healing_done": 0.03},
             connect=["frozen_blades"], total_slots=3,
             source="CoA free passive: 'Casting Ancestral Roar now increases "
                    "haste of party and raid members by 5% for 20 seconds'. "
                    "Party scope is not available to a talent (see Frozen "
                    "Blades), so the haste is the Barbarian's own and the node "
                    "also scales Ancestral Roar itself, which is the ability "
                    "CoA hangs it on."),
        node(A, "clanlords_totem", "Clanlord's Totem",
             "Increases all damage you deal by 2% per rank.",
             5, 2, 2, {"all_damage": 0.02}, connect=["ancestors_fury"],
             total_slots=3,
             source="CoA free passive: the totem makes 'allied players within "
                    "100 yds deal 35% AP additional damage as Frost'. The "
                    "placed totem is the cast ability of the same name; this "
                    "node is the Barbarian's own share of it, same split as "
                    "Frozen Blades and Uniting Voice."),

        node(A, "fury_of_the_north", "Fury of the North",
             "Something older than you takes the fight over for a while.",
             6, 0, 1, {"frost_damage_pct": 0.06, "haste": 3.0,
                       "max_health_pct": 0.04},
             node_type="active",
             connect=["rage_of_the_north", "uniting_voice", "clanlords_totem"],
             total_slots=1,
             source="Capstone. CoA: 'Increases the duration of the enrage "
                    "effect from your Ramhorn Rage by 6 sec and causes it to "
                    "increase your movement speed by 40% for its duration'. "
                    "Movement speed is nothing here and a duration extension "
                    "is a small capstone, so it carries the three things the "
                    "spec is built on at once: Frost, haste and the health to "
                    "stand in melee. max_health_pct is a FRACTION - 0.04 is "
                    "+4%, not +400%."),
    ],
    "Built from reference/coa_sidekick/SPEC_barbarian__ancestry.txt and the "
    "ancestry block of reference/coa_sidekick/talents/barbarian.json. CoA "
    "calls it 'the closest to retail Enhancement Shaman' - 'a melee DPS spec "
    "wearing support clothing via auras and a haste cooldown, not a healer' - "
    "and its own summary is 'You buff your side just by showing up.' Three "
    "translations run through the whole tree. The Tankard/Fill Level second "
    "resource does not exist (CLASS_RESOURCE_MAP gives this class one pool), "
    "so every empty-versus-full gate is gone and Fill Level and Liquid "
    "Courage become pool size and flat mitigation. The party auras are CAST "
    "abilities, because a talent effect can only ever reach its own owner, "
    "and the talent versions grant the Barbarian its share. And the Frost "
    "half of the kit runs on Frozen Warlord's attack-power conversion, which "
    "is CoA's own explanation for how a class with no magic deals Frost "
    "damage.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Barbarian",
        "_source_note": __doc__.strip().split("\n\n")[2].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/barbarian.json", ability_doc),
        (ROOT / "data/talents/barbarian_brutality.json", BRUTALITY),
        (ROOT / "data/talents/barbarian_headhunting.json", HEADHUNTING),
        (ROOT / "data/talents/barbarian_ancestry.json", ANCESTRY),
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
