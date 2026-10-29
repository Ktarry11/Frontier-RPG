#!/usr/bin/env python3
"""Author the Witch Doctor: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_witch_doctor.py [--apply]

The Witch Doctor is one of the twelve CoA classes that shipped with base
stats, armour (leather), weapon proficiency (staff/totem/dagger/fist/tome)
and a resource, and nothing else - no abilities, no talents, unselectable.
This builds the whole class. CoA calls it "an ancient, deep-seated aspect of
troll culture ... using terrible voodoo magic, wards and potions", and the
three specs are genuinely three different games:

  Voodoo         RANGED DPS  "Closest to Augmentation Evoker." A Shadow/
                             Nature/Fire caster whose support value is
                             protection and debuffs, not healing. PvE S.
  Brewing        HEALER      "Closest to Preservation Evoker, mechanically
                             rather than by vibe." A Cauldron of Ingredients
                             and Bases on top of a throw-heal loop.
  Shadowhunting  RANGED DPS  "Closest to a Survival Hunter built on a
                             shamanic support chassis." Ranged weapon,
                             Serpent Wards, a banked Spirit stack.

SOURCE. reference/coa_sidekick/CLASS_witch-doctor.txt, the three
SPEC_witch-doctor__*.txt pages, and reference/coa_sidekick/talents/
witch-doctor.json. Every ability and talent name below is a real CoA name
off those pages; nothing is invented to fill a slot. The CoA talent file has
~40 nodes per tree against Frontier's ~23 and three point gates against
Frontier's seven tiers, so each tree here is a SELECTION - the nodes that
actually carry the spec, laid out strongest-first with one capstone - not a
transcription.

RESOURCE. Mana, per CLASS_RESOURCE_MAP in combat/abilities.py (primary Mana,
no secondary). Mana is one of the resources whose cost is allowed to grow
per rank (_SCALES_COST_WITH_RANK), so costs scale alongside damage the way
shaman.json's and warlock.json's do rather than staying flat like a Rogue's.
Both series grow linearly to roughly 3x their rank-1 figure by the last rank
- shaman_lightning_bolt is 44 damage / 28 mana at rank 1 and 132 / 92 at
rank 9, and warlock_shadow_bolt is the same shape. Budget: a level 60 Witch
Doctor has 1085 Mana, so the biggest button here (Tiki Splash, 100 rising to
~220) is a real decision and nothing is uncastable.

SPIRITS. CoA's "Spirit" stack - a buff that "regenerates 7 health and mana,
repeating every 4 sec" and which Reclamation, Shadow Puppets and Loa Spirits
all collect - is not a resource in CLASS_RESOURCE_MAP, and adding one would
be an engine feature. It is implemented as real Mana returns instead:
Reclamation is a damage_and_restore_mana cast (the Stormbringer Discharge
mechanic), and the Spirit-flavoured talents grant mp5 or proc Mana.

WARDS, IDOLS AND EFFIGIES. The class's signature is placing things - Healing
Ward, Serpent Wards, Swift Idol, Cursed Effigy, the Voodoo Cauldron. Frontier
has no persistent-placed-object system; the shipped Shaman is the precedent
and every one of its totems is a plain instant cast with a _source note
saying so (searing_totem is a spell_dot, stoneskin_totem is a party buff).
These follow that convention exactly. Note also that Shaman's
totem_loadout - the one effect_type built for placed totems - reads
Character.totem_loadout, which Character.set_totem only populates from
combat/totems.py's TOTEM_ELEMENTS, a hardcoded map of six shaman_* ability
ids. A Witch Doctor totem_loadout ability would therefore always find an
empty loadout and fail, so there is none here. "totem" in this class's
weapon_types entry is the held-item type, not that system.

NO SUMMONS. Shadow Puppets, Serpent Wards and the War Golem are summons in
CoA. effect_type="summon_pet" needs a template in combat/pet_templates.py,
this pass may not add one, and the existing templates that fit mechanically
all carry a wrong name a player would read in the combat log (Mindbender,
Sentry Turret, Voidwalker). So the wards pulse damage as AoE spell_dots, the
puppets are a single-target spell_dot, and the War Golem is a real absorb
shield (absorb_pct_max_health), which is what its tooltip actually promises.
Each one says so in its own _source.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The level-1 rank schedule every class shares.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, cost, *, start=1, count=9, grow=2.0, cost_grow=2.2,
          heal_base=0, mana_pct=0):
    """Mana-costing rank table on the shipped caster curve.

    `base` and `cost` are the rank-1 figures. Both series climb linearly so
    the last rank sits at (1 + grow) and (1 + cost_grow) times rank 1 -
    roughly 3x, copying shaman.json/warlock.json rather than inventing a
    curve. Levels past the 9-rank schedule are spaced evenly to stay at or
    below 58 so every rank is reachable at the level 60 cap.

    heal_base: rank-1 heal for effect_type="damage_and_heal", which carries
        its healing on a separate `heal_value` rank key.
    mana_pct: % of max Mana returned, for damage_and_restore_mana's
        `mana_restore_pct` rank key. Flat across ranks - it is already a
        percentage of a pool that grows with level.
    """
    if start == 1:
        levels = RANK_LEVELS[:count]
    else:
        span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
        levels = [min(58, start + i * span) for i in range(count)]
    last = max(1, count - 1)
    out = []
    for i, level in enumerate(levels):
        entry = {
            "rank": i + 1,
            "level_req": level,
            "cost": int(round(cost * (1.0 + cost_grow * i / last))),
            "effect_value": int(round(base * (1.0 + grow * i / last))),
        }
        if heal_base:
            entry["heal_value"] = int(round(heal_base * (1.0 + grow * i / last)))
        if mana_pct:
            entry["mana_restore_pct"] = mana_pct
        out.append(entry)
    return out


def one(level, cost, value=100):
    """Single-rank table.

    value DEFAULTS TO 100, which matters: a buff/debuff's stat_mods are
    scaled by effect_value as a PERCENTAGE in Ability._apply_effect
    (`v * (self.effect_value / 100.0)`), so a buff shipped with
    effect_value 0 applies nothing at all. Damage and heal ranks pass their
    own real number.
    """
    return [{"rank": 1, "level_req": level, "cost": cost, "effect_value": value}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None, **extra):
    out = {
        "ability_id": f"witch_doctor_{aid}",
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
# Order is roughly the order a player meets them: the shared voodoo kit
# first, then each spec's own buttons.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A swing with whatever you are holding.", one(1, 0, 0),
            icon="ability_melee",
            source="Convention: every class ships a free rank-1 Attack."),

    # ---- shared class kit -------------------------------------------------
    ability("malefic_wrath", "Malefic Wrath", "spell_damage",
            "A fistful of ill will, thrown hard.",
            ranks(44, 28), target_type="enemy", damage_school="shadow",
            source="CoA class tree: 'when you cast Malefic Wrath and Loa's "
                   "Brew the ward will also cast it on your target'. The "
                   "class's baseline Shadow nuke, on shaman_lightning_bolt's "
                   "exact 9-rank curve."),
    ability("loas_brew", "Loa's Brew", "heal",
            "A mouthful of something bitter that puts an ally back together.",
            ranks(56, 40), cooldown=1, target_type="ally",
            source="CoA class tree names Loa's Brew alongside Malefic Wrath "
                   "as what Mimic Ward echoes, and it is not a talent node in "
                   "any of the three spec trees, so it is a class ability. "
                   "Voodoo's page says that spec has 'no ally heal' - true of "
                   "its TREE, which spends nothing on healing."),
    ability("shrinking_jinx", "Shrinking Jinx", "debuff",
            "The target's arms stop reaching as far as they used to.",
            ranks(100, 22, start=6, count=4, grow=0.6, cost_grow=1.6),
            cooldown=4, duration=3, stat_mods={"attack_power": -45},
            target_type="enemy",
            source="CoA class tree: 'When your Shrinking Jinx is dispelled it "
                   "now applies Misery to the dispeller'. The jinx itself "
                   "shrinks what the target can swing."),
    ability("hex_of_malice", "Hex of Malice", "spell_dot",
            "A curse that settles in and keeps working.",
            ranks(95, 30, start=8, count=6), cooldown=2, duration=4,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Curse an enemy, dealing shadow damage and an "
                   "additional 96 Shadow damage over 24 seconds.' The DoT all "
                   "three specs keep rolling - warlock_corruption's curve."),
    ability("healing_ward", "Healing Ward", "hot",
            "A ward planted in the dirt that keeps everyone standing near it "
            "on their feet.",
            ranks(60, 50, start=10, count=6), cooldown=3, duration=4,
            target_type="party",
            source="CoA: 'Drop a Healing Ward near you for 1 minute, healing "
                   "8 nearby allies within 30 yds for Spirit every 3 sec'. "
                   "Both DPS specs' pages call this the class pool's only ally "
                   "heal. A placed, pulsing ward becomes an instant party HoT, "
                   "the same simplification every shipped Shaman totem uses."),
    ability("lethargy_jinx", "Lethargy Jinx", "debuff",
            "Everything the target does arrives late, and nothing that is "
            "done for them helps much.",
            ranks(100, 25, start=12, count=4, grow=0.6, cost_grow=1.6),
            cooldown=3, duration=3,
            stat_mods={"haste": -25, "healing_taken_pct": -20},
            target_type="enemy",
            source="CoA class tree: 'Jinx of Decay - Your Lethargy Jinx now "
                   "also reduces the target's periodic healing received by "
                   "-30%'. healing_taken_pct is the engine's real anti-heal "
                   "key, read recipient-side in Character.heal."),
    ability("hexbreak", "Hexbreak", "dispel",
            "You talk the curse off them.",
            one(14, 32, 0), cooldown=1, target_type="ally",
            dispel_type="curse",
            source="CoA: 'Dispel duty is single-curse removal through "
                   "Hexbreak'. 'Blessing of Hir'eek - Your Hexbreak now "
                   "removes an additional curse effect' is the class tree's "
                   "dispel_count upgrade, which is a talent, not this."),
    ability("mirage", "Mirage", "buff",
            "You step out of your own outline and leave it standing there.",
            one(16, 30), cooldown=8, duration=2,
            stat_mods={"threat_generation_pct": -60, "dodge": 10},
            target_type="self",
            source="CoA: 'Become invisible for 20 seconds, gaining 5 Spirits, "
                   "leaving a copy of yourself behind, and reducing threat "
                   "each second.' Both DPS pages call the class's escapes "
                   "'threat drops, they do not move you', so this is threat "
                   "and avoidance rather than a blink."),
    ability("shadowflare", "Shadowflare", "spell_damage",
            "Dark fire goes up out of the ground under a whole pack of them.",
            ranks(58, 55, start=18, count=5), cooldown=3,
            target_type="enemy_aoe", max_targets=5, damage_school="shadow",
            source="CoA: 'spread Hex of Malice with Shadowflare', 'Dealing "
                   "damage with Shadowflare now applies Hex of Malice if it "
                   "strikes at least 3 enemies'. The shared AoE. NOTE: the "
                   "engine's AoE flag is target_type='enemy_aoe' plus "
                   "max_targets - a player Ability never reads is_aoe, which "
                   "_ability_from_data does not pass to the constructor."),
    ability("voljins_vigil", "Vol'jin's Vigil", "buff",
            "You hold still and breathe the way he taught, and the hits stop "
            "mattering so much.",
            one(20, 40), cooldown=10, duration=3,
            stat_mods={"damage_taken_pct": -0.25}, target_type="self",
            proc={"trigger": "on_damage_taken", "chance": 100, "icd": 0,
                  "heal_flat": 45},
            source="CoA: 'Embrace the way of Vol'jin, reducing your damage "
                   "taken by -25% and healing you for 2% of your maximum "
                   "health every 1 sec for 10 seconds.' Both halves are real: "
                   "the mitigation as a stat_mod, the trickle as an "
                   "on_damage_taken heal proc on the resulting buff."),
    ability("amphibimorph", "Amphibimorph", "debuff",
            "The target is a frog. It has opinions about this but no way to "
            "express them.",
            one(22, 35), cooldown=6, duration=2, stat_mods={"haste": -30},
            target_type="enemy", is_stun=True,
            source="CoA: 'Transform enemies at target location into a frog, "
                   "making them unable to attack or cast spells, and slowing "
                   "their movement speed'. is_stun is the engine's real "
                   "skip-their-turn flag (TurnMeter refuses to fill for a "
                   "stunned combatant)."),
    ability("allcure_elixir", "Allcure Elixir", "dispel",
            "Clears out whatever they swallowed, breathed, or were bitten by.",
            one(24, 35, 0), cooldown=1, target_type="ally",
            dispel_type=["poison", "disease"],
            source="CoA: 'Allcure Elixir clears poison, disease and curse "
                   "effects off one ally'. Curse is already Hexbreak's job, so "
                   "this covers the other two rather than making Hexbreak "
                   "redundant. 'For Da Loa!' upgrades it to the group-wide "
                   "Mass Allcure Elixir, which is a class-tree pick, not this."),
    ability("slither", "Slither", "buff",
            "You come apart into something long and low, and whatever was "
            "holding you is holding nothing.",
            one(26, 25), cooldown=6, duration=2,
            stat_mods={"dodge": 25, "haste": 15}, target_type="self",
            source="CoA: 'Transform into a serpent, removing all movement "
                   "impairing effects and increasing movement speed by 80% ... "
                   "chance to be hit by ranged attacks and spells is reduced'. "
                   "No movement-impairment category exists on the player side, "
                   "so the avoidance half carries the node."),
    ability("stasis_ward", "Stasis Ward", "debuff",
            "A ward that stops everything close to it where it stands.",
            one(28, 50), cooldown=8, duration=1, stat_mods={"haste": -20},
            target_type="enemy_aoe", max_targets=4, is_stun=True,
            source="CoA class tree: 'Touch of Mueh'zala - Increases the "
                   "duration of Stasis Ward's stun effect by 1 sec', so the "
                   "ward stuns. The class's only AoE stun."),
    ability("swift_idol", "Swift Idol", "buff",
            "An idol goes in the ground and nobody around it drags their feet.",
            one(30, 35), cooldown=6, duration=3,
            stat_mods={"haste": 12, "dodge": 5}, target_type="party",
            source="CoA: 'Drop a Swift Idol near you for 10 seconds. Allies "
                   "within 30 yds gain 25% increased movement speed and their "
                   "chance to resist movement impairing effects is increased'. "
                   "Movement speed has no combat meaning in a turn engine, so "
                   "it lands as Haste, which is what moving faster buys."),
    ability("mimic_ward", "Mimic Ward", "buff",
            "Something shaped roughly like you stands at your shoulder and "
            "repeats you.",
            ranks(100, 45, start=32, count=3, grow=0.5, cost_grow=1.0),
            cooldown=10, duration=3,
            stat_mods={"shadow_spell_power": 25, "spell_power": 15},
            target_type="self",
            source="CoA: 'Summon a mimic ward for 12 seconds. For the duration "
                   "when you cast Malefic Wrath and Loa's Brew the ward will "
                   "also cast it on your target.' There is no "
                   "repeat-my-last-cast mechanic in the engine, so the window "
                   "lands as the spell power the echo would have been worth. "
                   "The cast-echo is the one part of this kit with no honest "
                   "equivalent."),
    ability("cursed_effigy", "Cursed Effigy", "buff",
            "A bundle of sticks and hair with your enemies' luck tied into it.",
            one(34, 45), cooldown=10, duration=3,
            stat_mods={"physical_damage_taken_pct": -8,
                       "magic_damage_taken_pct": -8},
            target_type="party",
            source="CoA: 'Drop a Cursed Effigy near you for 15 seconds. "
                   "Enemies within 15 yds are unable to critically strike.' "
                   "GAP: a monster's crit_chance is a plain template attribute "
                   "(entities/monster.py) that no status effect touches, so "
                   "crit suppression has no hook at all. Implemented from the "
                   "other side - the party takes less damage, which is what "
                   "losing enemy crits is worth."),
    ability("power_wuju", "Power Wuju", "buff",
            "You hand out the good stuff.",
            ranks(100, 45, start=36, count=3, grow=0.5, cost_grow=1.0),
            cooldown=8, duration=4,
            stat_mods={"spell_power": 30, "attack_power": 30, "spirit": 8},
            target_type="party",
            source="CoA class tree: 'Loa Empowerment - Reduces the cost of "
                   "your Wujus by -50% and increases the effectiveness of "
                   "Power Wuju by 20%'. A Wuju is a thrown buff, so it buffs "
                   "both halves of a party."),
    ability("death_draught", "Death Draught", "buff",
            "You drink it, you stop, and for a moment nothing in the room "
            "thinks you are worth the trouble.",
            one(38, 0), cooldown=14, duration=1,
            stat_mods={"damage_taken_pct": -0.5,
                       "threat_generation_pct": -100},
            target_type="self",
            source="CoA: 'Drink a potent voodoo draught that slows your body "
                   "to a deathlike stillness ... causing you to feign death "
                   "which may trick enemies into ignoring you.' No feign-death "
                   "mechanic exists, so one turn of heavy mitigation and a "
                   "total threat drop stands in for it. Free to cast, like the "
                   "real one."),
    ability("veil_of_darkness", "Veil of Darkness", "debuff",
            "A shadow settles over them and everything you send lands harder.",
            ranks(100, 50, start=40, count=3, grow=0.4, cost_grow=0.8),
            cooldown=8, duration=4, stat_mods={"damage_taken_pct": 0.12},
            target_type="enemy",
            source="CoA: 'Envelop a target in a shadowy voodoo veil, "
                   "increasing the damage you deal to them by 15% for 15 "
                   "seconds.' damage_taken_pct on the target is read raw as a "
                   "fraction in Character.take_damage. It amplifies everyone's "
                   "damage, not only yours - the engine has no "
                   "per-attacker-only amplification."),
    ability("big_bad_voodoo", "Big Bad Voodoo", "buff",
            "The drums start, and for a little while nothing in your line "
            "can be killed. Nothing in your line can kill much either.",
            one(44, 60), cooldown=15, duration=3,
            stat_mods={"damage_taken_pct": -0.3, "damage_dealt_pct": -25},
            target_type="party",
            source="CoA class tree: 'One Armed Waltz - Big Bad Voodoo now "
                   "only reduces damage dealt by 25% and reduces damage taken "
                   "by an additional -5%', which says the baseline trades your "
                   "damage for survival. Both sides are real keys: "
                   "damage_taken_pct raw, damage_dealt_pct in percentage "
                   "points through Ability._damage_multiplier."),

    # ---- Voodoo -----------------------------------------------------------
    ability("bad_juju", "Bad Juju", "spell_damage",
            "A bolt of something that was never meant to be aimed at people.",
            ranks(62, 36, start=10, count=7), cooldown=2, target_type="enemy",
            damage_school="shadow",
            source="CoA: 'Bad Juju on cooldown (main nuke ...)'. 'Hurl a bolt "
                   "of dark magic at an enemy, dealing Spirit Shadow damage, "
                   "scaling with your Spirit.' The spec's centrepiece."),
    ability("hexfire", "Hexfire", "spell_damage",
            "Fire that burns colder than it should and finds the seams in "
            "whatever you have already cursed.",
            ranks(76, 48, start=20, count=6), cooldown=3, target_type="enemy",
            damage_school="fire",
            source="CoA: 'Blast an enemy with hexfire, dealing Fire damage, "
                   "scaling with your Spirit'; 'Detonate Puppeteer's Threads "
                   "with Hexfire for burst'. The thread-snap has no engine "
                   "hook, so Hexfire is a straight Fire payoff nuke."),
    ability("shadow_puppets", "Shadow Puppets", "spell_dot",
            "Small flat things peel off your shadow and go to work.",
            ranks(84, 44, start=24, count=5), cooldown=4, duration=3,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Summon a Shadow Puppet that collects a Spirit and "
                   "rushes towards your target, dealing shadow damage, "
                   "repeating every 1 sec for 3 seconds.' A summon whose whole "
                   "job is three ticks of damage on one target, so it is a "
                   "spell_dot rather than a pet - see the module docstring on "
                   "why no summon_pet template fits."),
    ability("malignant_jinx", "Malignant Jinx", "debuff",
            "The next word they try to say turns on them.",
            one(26, 35), cooldown=6, duration=2,
            stat_mods={"damage_dealt_pct": -30}, target_type="enemy",
            source="CoA: 'Curse an enemy for 8 seconds, causing their next "
                   "spell cast to silence them for 5 sec'; 'Malignant Jinx "
                   "counters a dangerous cast with a silence'. GAP: there is "
                   "no silence or school-lockout category, and is_stun would "
                   "make this a stun, which it is not. A hard cut to what they "
                   "deal is the nearest honest thing."),
    ability("war_golem", "War Golem", "buff",
            "You build something out of mud and malice and stand behind it.",
            ranks(100, 50, start=30, count=4, grow=0.45, cost_grow=0.9),
            cooldown=12, duration=2, absorb_pct_max_health=0.22,
            stat_mods={"magic_damage_taken_pct": -10}, target_type="self",
            source="CoA: 'Summon a War Golem for 10 seconds, absorbing damage "
                   "dealt to you based on your Intellect, and redirecting "
                   "harmful spells cast on nearby allies to itself.' The absorb "
                   "is real (absorb_pct_max_health, the same field Cultist's "
                   "Eldritch Bastion uses). The ally-spell redirect has no "
                   "engine hook, so the magic mitigation stands in for it."),
    ability("puppeteers_grasp", "Puppeteer's Grasp", "enable_instant_cast",
            "You go thin and sideways, and casting stops needing you to "
            "stand still.",
            one(34, 30, 0), cooldown=8, target_type="self",
            source="CoA: 'Transform into a malignant spirit for 30 seconds, "
                   "allowing you to cast Malefic Wrath and Bad Juju while "
                   "moving, and periodically granting you a Spirit every 2 "
                   "sec.' Nothing in the engine costs movement, so "
                   "cast-while-moving becomes the real thing it buys: the next "
                   "cast is free of its turn."),
    ability("voice_of_bwonsamdi", "Voice of Bwonsamdi", "buff",
            "You let him speak through you. He is not gentle about it.",
            one(40, 55), cooldown=15, duration=3,
            stat_mods={"shadow_spell_power": 40, "crit_chance_spell": 8,
                       "damage_dealt_pct": 15},
            target_type="self",
            source="CoA: 'Let the spirit of Bwonsamdi possess you for 15 "
                   "seconds. Dealing periodic damage unleashes a trapped "
                   "voodoo spirit at enemies'; 'Voice of Bwonsamdi is your big "
                   "damage cooldown'."),

    # ---- Brewing ----------------------------------------------------------
    ability("potion_toss", "Potion Toss", "heal",
            "You fill one from the pot and throw it without looking.",
            ranks(44, 32, start=10, count=6), cooldown=3, target_type="ally",
            is_instant=True,
            source="CoA: 'the instant, short-cooldown Potion Toss'; 'Fill a "
                   "potion from your Cauldron, and toss it at a friendly "
                   "target'. Splash On 'Em shaves its cooldown, which is why "
                   "it ships at 3 turns and not 1."),
    ability("spirit_in_a_bottle", "Spirit in a Bottle", "damage_and_heal",
            "You uncork it at them. Something leaves, and on its way out it "
            "patches up whoever is worst off behind you.",
            ranks(40, 45, start=16, count=6, heal_base=64), cooldown=3,
            target_type="enemy", heal_scope="lowest_ally",
            source="CoA: 'Spirit in a Bottle heals an ally while chipping and "
                   "debuffing nearby enemies off the same cast, functionally "
                   "the same trick as Living Flame'. damage_and_heal is cast "
                   "at an ENEMY and heals off the damage, which is exactly "
                   "this shape."),
    ability("splash_potion", "Splash Potion", "heal",
            "You throw the whole bottle into the middle of them.",
            ranks(64, 65, start=22, count=5), cooldown=4, target_type="party",
            source="CoA: 'Fill a splash potion from your Cauldron, and toss it "
                   "at a location, healing up to 8 allies'; 'Use Splash Potion "
                   "for stacked-group healing'."),
    ability("mojo_beam", "Mojo Beam", "hot",
            "A steady line of mojo from you to them, held open as long as "
            "you can hold it.",
            ranks(100, 55, start=26, count=5), cooldown=3, duration=4,
            target_type="ally",
            source="CoA: 'Bring mojo to an ally, healing for SP every 1 sec "
                   "for 4 seconds. While channeling, you can instantly cast "
                   "Potion Toss, Splash Potion and Spirit in a Bottle'. GAP: "
                   "there is no channel state, so the weave window is gone and "
                   "this is a four-turn single-target HoT - which is what the "
                   "channel's healing actually was."),
    ability("ingredient_jungle_shrooms", "Ingredient: Jungle Shrooms", "hot",
            "Shrooms go in the pot. Everyone gets a little better for a "
            "while.",
            ranks(70, 55, start=30, count=4), cooldown=6, duration=4,
            target_type="party", exclusive_group="witch_doctor_ingredient",
            source="CoA: 'Brew Jungle Shrooms into your Cauldron. Cauldron: "
                   "Heal up to 8 allies within 30 yds for healing every 8 "
                   "sec'; 'a rolling Jungle Shrooms heal-over-time'. The three "
                   "Ingredients share one exclusive_group because CoA says "
                   "'Only 1 of each Ingredient can be active at a time' and "
                   "the Mojo swap talents swap them in pairs."),
    ability("ingredient_frog_bones", "Ingredient: Frog Bones", "buff",
            "Bones in the pot. Whatever is coming lands softer.",
            ranks(100, 55, start=30, count=4, grow=0.45, cost_grow=0.9),
            cooldown=6, duration=4, absorb_pct_max_health=0.12,
            stat_mods={"damage_taken_pct": -0.06}, target_type="party",
            exclusive_group="witch_doctor_ingredient",
            source="CoA: 'Cauldron: Grants allies within 40 yds 3% reduced "
                   "damage taken. Potion: Grants target ally an absorption "
                   "shield, absorbing Spirit damage.' Both halves are real "
                   "here - the mitigation and the shield."),
    ability("ingredient_bloodthistle", "Ingredient: Bloodthistle", "buff",
            "Thistle in the pot. What your allies deal starts coming back to "
            "them.",
            ranks(100, 55, start=30, count=4, grow=0.45, cost_grow=0.9),
            cooldown=6, duration=4, stat_mods={"healing_taken_pct": 8},
            target_type="party", exclusive_group="witch_doctor_ingredient",
            proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                  "leech_pct": 0.05},
            source="CoA: 'Cauldron: Allies within 40 yds receive 8% increased "
                   "healing. Potion: Causes target ally to leech 5% of all "
                   "damage they deal.' Both halves are real: healing_taken_pct "
                   "recipient-side, and leech_pct, the engine's own "
                   "damage-done-also-heals proc payload."),
    ability("voodoo_cauldron", "Voodoo Cauldron", "buff",
            "The pot goes down where the tank is standing. Everything poured "
            "into that circle goes further.",
            ranks(100, 60, start=36, count=3, grow=0.4, cost_grow=0.8),
            cooldown=8, duration=4,
            stat_mods={"healing_taken_pct": 20, "mp5": 4},
            target_type="party",
            source="CoA: 'Place down a Voodoo Cauldron for 15 seconds, "
                   "increasing allies' healing received by 20% while near the "
                   "cauldron'; 'drop Voodoo Cauldron ... on the tank's stack "
                   "point'. The heals-received zone is a real key; the pulse "
                   "is Jungle Shrooms' job and not duplicated here."),
    ability("base_beast_blood", "Base: Beast Blood", "buff",
            "Blood in the base. The hits still land, they just stop arriving "
            "all at once.",
            one(38, 50), cooldown=10, duration=3,
            stat_mods={"physical_damage_taken_pct": -15}, target_type="party",
            exclusive_group="witch_doctor_base",
            source="CoA: 'Infuse your Cauldron with Beast Blood for 10 "
                   "seconds, causing 15% of the direct Physical damage taken "
                   "by allies within 40 yds to instead be dealt over time. "
                   "Only 1 Base can be active at a time.' GAP: there is no "
                   "convert-a-hit-into-a-DoT mechanic, so the 15% is simply "
                   "removed rather than deferred. The two Bases share an "
                   "exclusive_group, as CoA requires."),
    ability("base_crystal_water", "Base: Crystal Water", "buff",
            "Clean water in the base. Everything you heal leaves a skin "
            "behind it.",
            one(38, 50), cooldown=10, duration=3,
            absorb_pct_max_health=0.10,
            stat_mods={"magic_damage_taken_pct": -10}, target_type="party",
            exclusive_group="witch_doctor_base",
            source="CoA: 'Infuse your Cauldron with Crystal Water for 10 "
                   "seconds, causing allies within 40 yds to be shielded for "
                   "20% of their healing taken'. Shield-off-healing has no "
                   "hook, so the shield is sized off the recipient's own health "
                   "instead - same field, honest magnitude."),
    ability("tiki_splash", "Tiki Splash", "heal",
            "You break the big one over the whole group.",
            ranks(150, 100, start=44, count=2), cooldown=12,
            target_type="party",
            source="CoA lists Tiki Splash among Brewing's 23-TE tier-6 picks "
                   "with no tooltip text ('see builder tooltip'), so the name "
                   "is real and the mechanic is read off its slot: the spec's "
                   "emergency group heal, which the rotation otherwise lacks "
                   "('Hold Master Mixologist as the group heal-burst and "
                   "wipe-prevention amplify window')."),
    ability("master_mixologist", "Master Mixologist", "buff",
            "Everything in the pot is suddenly twice what it was.",
            one(46, 45), cooldown=15, duration=3,
            stat_mods={"healing_power_pct": 40, "haste": 10},
            target_type="self",
            source="CoA: 'For 10 seconds, the effectiveness of all Cauldron "
                   "effects and Ingredients is increased by 100% and you can "
                   "cast Spirit in a Bottle while moving.' healing_power_pct "
                   "takes percentage POINTS (one of the ten keys "
                   "Character._recalculate_derived_stats divides by 100), so "
                   "40 is +40%, not +4000%."),

    # ---- Shadowhunting ----------------------------------------------------
    ability("reclamation", "Reclamation", "damage_and_restore_mana",
            "A quick arrow, and something comes back down the line with it.",
            ranks(40, 30, start=10, count=7, mana_pct=4), target_type="enemy",
            damage_school="nature", is_instant=True, icon="ability_melee",
            source="CoA: 'Shoot a quick voodoo arrow at an enemy dealing 100% "
                   "Ranged Weapon Damage plus 15 as Nature damage and "
                   "collecting a Spirit. Spirit: Regenerates 7 health and mana "
                   "... Usable while moving.' Spirits are not a resource in "
                   "CLASS_RESOURCE_MAP, so the Spirit collection is a real "
                   "Mana return - 4% of 1085 at level 60 against a 30-ish "
                   "cost, which is the net-positive filler CoA describes."),
    ability("malefic_arrow", "Malefic Arrow", "ranged_damage",
            "The arrow is ordinary. What is wrapped around it is not.",
            ranks(70, 34, start=12, count=6), cooldown=2, target_type="enemy",
            damage_school="nature", icon="ability_melee",
            source="CoA: 'Transforms your Malefic Wrath into Malefic Arrow. "
                   "Launch a voodoo arrow at an enemy, dealing 85% Ranged "
                   "Weapon Damage plus nature SP as Nature damage, healing you "
                   "equal to 40% of the damage dealt.' The self-heal is the "
                   "class tree's Devotion to Bwonsamdi, so it lives in the "
                   "tree as a leech proc rather than being baked in twice."),
    ability("spirit_glaive", "Spirit Glaive", "spell_damage",
            "Two glaives that are not quite there go through the line and "
            "come back.",
            ranks(60, 50, start=20, count=5), cooldown=3,
            target_type="enemy_aoe", max_targets=3, damage_school="shadow",
            source="CoA: 'Toss spectral glaives that strikes enemies it passes "
                   "through, dealing shadow damage, and reducing their Shadow "
                   "Resistance by 61 for 5 seconds. Usable while moving.' The "
                   "resistance shred would need a debuff on top of a damage "
                   "cast, which no single effect_type does, so the pass-through "
                   "cleave carries the ability."),
    ability("spirit_shock", "Spirit Shock", "debuff",
            "You get a hand around the part of them that was about to speak.",
            one(24, 35), cooldown=6, duration=2,
            stat_mods={"haste": -45, "damage_dealt_pct": -20},
            target_type="enemy",
            source="CoA: 'Shock an enemy's spirit, silencing them for 4 "
                   "seconds and interrupting non-player spellcasting'. GAP: no "
                   "silence or interrupt category exists. A heavy Haste cut is "
                   "the engine's real delay-their-turn lever (TurnMeter reads "
                   "Haste off status effects), which is the closest thing to "
                   "taking a cast away from them."),
    ability("call_of_sseratus", "Call of Sseratus", "spell_dot",
            "Four wards come up out of the ground around you and start "
            "biting.",
            ranks(70, 55, start=26, count=4), cooldown=6, duration=4,
            target_type="enemy_aoe", max_targets=4, damage_school="nature",
            source="CoA: 'Summon 4 Serpent Wards near you for 15 seconds'; "
                   "'Drop your Serpent Wards before or on the pull so they add "
                   "sustained damage through the fight.' Placed pulsing wards "
                   "become an AoE spell_dot, exactly as shaman_magma_totem "
                   "does, and not a summon_pet - see the module docstring."),
    ability("spirit_eclipse", "Spirit Eclipse", "spell_damage",
            "Everything you have been saving goes out at once and bursts on "
            "arrival.",
            ranks(90, 70, start=32, count=4), cooldown=5,
            target_type="enemy_aoe", max_targets=4, damage_school="shadow",
            source="CoA: 'Unleash your Spirits on an enemy, dealing shadow "
                   "damage for each active Spirit. Each Spirit explodes on "
                   "impact, dealing damage to other nearby enemies.' Without a "
                   "Spirit stack to scale off, it is a fixed hard-hitting "
                   "cleave on a cooldown rather than a variable dump."),
    ability("shadowstalker", "Shadowstalker", "buff",
            "You step into the dark between two trees and nothing follows "
            "you in.",
            one(36, 20), cooldown=12, duration=2,
            stat_mods={"dodge": 30, "haste": 15,
                       "threat_generation_pct": -80},
            target_type="self",
            source="CoA: 'Disappear into darkness, entering an improved "
                   "stealth mode, clearing all harmful effects, and increasing "
                   "movement speed by 50%'. GAP: a buff cannot also dispel, so "
                   "the clear-all-harmful-effects half is gone - which matters, "
                   "because CoA calls it 'the entire answer to CC' for this "
                   "spec. The disengage half is real."),
    ability("shadow_avatar", "Shadow Avatar", "buff",
            "You stop being quite a person for a few seconds.",
            one(42, 50), cooldown=15, duration=3,
            stat_mods={"damage_dealt_pct": 12, "haste": 10},
            target_type="self",
            source="CoA: 'Lesser Shadow Avatar - Increases magic damage dealt "
                   "by 10% and reduces the cooldown of Spirit Glaive by 20% "
                   "every 1 sec'; 'then Shadow Avatar ... and Fool's Play'. "
                   "damage_dealt_pct is school-agnostic in this engine (see "
                   "Ability._damage_multiplier), so 'magic damage dealt' lands "
                   "as all damage dealt."),
    ability("frenzied_spirits", "Frenzied Spirits", "buff",
            "You spend the lot. For a few seconds you cannot miss and you "
            "cannot be worn down.",
            one(46, 45), cooldown=12, duration=3,
            stat_mods={"crit_chance_physical": 10, "crit_chance_spell": 10},
            target_type="self",
            proc={"trigger": "on_damage_cast", "chance": 100, "icd": 0,
                  "leech_pct": 0.02},
            source="CoA: 'Consumes your Spirits to increase your ranged "
                   "critical strike rating by 10, critical damage by 5%, and "
                   "causing you to heal for 2% of all damage dealt for each "
                   "Spirit consumed.' The crit and the leech are both real; "
                   "crit_damage_physical is NOT - it is read only through "
                   "get_talent_effect, so it does nothing in a buff's "
                   "stat_mods and is left to the tree instead."),
]


# ============================================================ talent helpers

def node(tree, tid, name, description, tier, slot, max_points, effects,
         *, node_type="passive", connect=None, proc=None, source=None,
         total_slots=4):
    """One talent node. `slot` is 0-based across the tier's row.

    Hex layout copies the shipped trees: hex_y = -6 + 2*tier, hex_x spaced
    by 2 and centred on the row, so tiers narrow toward the capstone.
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


# ================================================================== Voodoo
V = "witch_doctor_voodoo"
VOODOO = tree(
    V, "Witch Doctor Voodoo",
    "Ranged Shadow, Nature and Fire caster. Keeps Hex of Malice rolling, "
    "chains Bad Juju, Malefic Wrath and Hexfire into it, and supports the "
    "party by amplifying and absorbing rather than healing.",
    [
        node(V, "staff_of_the_coven", "Staff of the Coven",
             "Increases your Spirit by 2% and your spell hit chance by 1% "
             "per rank.",
             0, 0, 5, {"spirit_pct": 2.0, "hit_rating": 1},
             source="CoA: 'Increases your Spirit by 8% and your hit chance by "
                    "2%' at 3 ranks. Spirit leads this spec's stat priority "
                    "(Spell Hit > Spirit > Spell Power), which is unusual for "
                    "a damage tree and is what Voodoo Power below is for."),
        node(V, "stranglethorn_style", "Stranglethorn Style",
             "Increases your spell critical strike chance by 1% per rank and "
             "reduces the threat your spells generate by 3%.",
             0, 1, 5, {"crit_chance_spell": 1.0, "threat_generation_pct": -0.03},
             source="CoA: 'Increases your critical strike chance by 4% and "
                    "reduces threat generated by your Voodoo spells by -20%'. "
                    "threat_generation_pct as a TALENT effect is a fraction, "
                    "unlike the same key in an ability's stat_mods."),
        node(V, "dark_magic", "Dark Magic",
             "Increases the damage of Malefic Wrath by 4% per rank.",
             0, 2, 5, {"ability_witch_doctor_malefic_wrath_damage": 0.04},
             source="CoA: 'Reduces the cast time of Malefic Wrath and Bad Juju "
                    "by -0.3 sec'. Cast time is not a concept in a turn engine, "
                    "so the node carries the throughput that shorter casts "
                    "would have bought."),
        node(V, "loa_spirits", "Loa Spirits",
             "Restores 2 Mana every 5 seconds and increases your Spirit by 1% "
             "per rank.",
             0, 3, 5, {"mp5": 2, "spirit_pct": 1.0},
             source="CoA: 'Damage dealt and healing done now has a 8% chance "
                    "to collect a Spirit. In addition, each active Spirit now "
                    "increases your Spirit by 2%.' Spirits are not a resource "
                    "here (see the module docstring), so the stack becomes "
                    "what it was for: Mana back, and more Spirit."),

        node(V, "voodoo_power", "Voodoo Power",
             "Grants spell damage equal to 2% of your Spirit per rank.",
             1, 0, 5, {"spell_damage_from_spirit_pct": 0.02},
             connect=["staff_of_the_coven"],
             source="CoA: 'Increases your spell damage by 50% of your Spirit "
                    "and your spell hit rating by 5% of your Spirit.' A real "
                    "<target>_from_<source>_pct conversion, resolved against "
                    "the shared STAT_CONVERSION maps in character.py. This is "
                    "the node that makes Spirit a damage stat."),
        node(V, "zalazanes_malice", "Zalazane's Malice",
             "Increases the damage of Hex of Malice by 5% per rank.",
             1, 1, 3, {"ability_witch_doctor_hex_of_malice_damage": 0.05},
             connect=["stranglethorn_style"],
             source="CoA: 'Increases the damage of Hex of Malice by 15% and "
                    "the duration of Jinxes by 2 sec'; the rotation is built "
                    "on 'Keep Zalazane's Malice up'."),
        node(V, "overflowing_juju", "Overflowing Juju",
             "Increases your Shadow spell power by 4 per rank.",
             1, 2, 3, {"shadow_spell_power": 4}, connect=["dark_magic"],
             source="CoA: 'Increases the spell power scaling of Malefic Wrath, "
                    "Shadowflare, and Bad Juju by 20%' - all three are Shadow, "
                    "so the node grants Shadow spell power directly."),
        node(V, "its_da_voodoo", "It's Da Voodoo",
             "Increases the damage of Shadowflare by 5% per rank.",
             1, 3, 5, {"ability_witch_doctor_shadowflare_damage": 0.05},
             connect=["loa_spirits"],
             source="CoA ships this one as 'Increases the damage of Shadowflare "
                    "by 0%' - a real bug in the source data. The intent is "
                    "obvious from the name and slot, so it carries a real "
                    "number here."),

        node(V, "ritual_hexing", "Ritual Hexing",
             "Increases the Shadow damage you deal by 2% per rank.",
             2, 0, 3, {"shadow_spell_damage": 0.02},
             connect=["voodoo_power"],
             source="CoA: 'Increases the damage of Bad Juju, Malefic Wrath and "
                    "Hexfire by 10% against enemies affected by Hex of "
                    "Malice.' Conditional-on-a-debuff damage has no hook, so "
                    "it lands as flat Shadow damage. shadow_spell_damage is one "
                    "of the school keys the engine assembles at runtime."),
        node(V, "growing_malice", "Growing Malice",
             "Increases the damage of your damage-over-time effects by 3% per "
             "rank.",
             2, 1, 5, {"dot_damage": 0.03}, connect=["zalazanes_malice"],
             source="CoA: 'Each tick of Hex of Malice increases the damage of "
                    "the next tick on the enemy by 3%, stacking 10 times.' "
                    "Ramping per-tick damage is not modellable, so the whole "
                    "ramp is paid out flat."),
        node(V, "hexplosion", "Hexplosion",
             "Your critical strikes increase your haste by 4 per rank for "
             "two turns.",
             2, 2, 3, {}, connect=["overflowing_juju"],
             proc={"trigger": "on_crit", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_hexplosion",
                       "name": "Hexplosion",
                       "effect_type": "buff",
                       "duration": 2,
                       "stat_mods": {"haste": 4.0},
                       "on_target": False}},
             source="CoA: 'Your offensive critical strikes now increase your "
                    "haste by 20% for 6 seconds.'"),
        node(V, "jindos_wrath", "Jin'do's Wrath",
             "Increases your spell critical strike damage by 4% per rank.",
             2, 3, 3, {"crit_damage_spell": 0.04}, connect=["its_da_voodoo"],
             source="CoA: 'Increases the critical strike chance and critical "
                    "damage of Hexfire by 25%.' crit_damage_spell is read "
                    "through get_talent_effect only, which is why it belongs "
                    "in the tree and not in a buff's stat_mods."),

        node(V, "prolonged_malice", "Prolonged Malice",
             "Hex of Malice lasts 1 turn longer per rank.",
             3, 0, 2, {"ability_witch_doctor_hex_of_malice_duration": 1},
             connect=["ritual_hexing"],
             source="CoA: 'Increases the duration of your Hex of Malice by 6 "
                    "sec and the range of your offensive Voodoo spells by 6 "
                    "yds'. Range is not a concept here; duration is."),
        node(V, "voodoo_strings", "Voodoo Strings",
             "Increases the damage of Bad Juju by 5% and of your Nature "
             "damage-over-time effects by 2% per rank.",
             3, 1, 3, {"ability_witch_doctor_bad_juju_damage": 0.05,
                       "nature_dot_damage": 0.02},
             connect=["growing_malice"],
             source="CoA: 'When Bad Juju is used on enemies affected by "
                    "Puppeteer's Threads, it strikes an additional time every "
                    "1 sec for 30% of the damage dealt over 3 seconds as "
                    "Nature damage.' Both halves of that - a bigger Bad Juju "
                    "and a Nature tail - without the thread condition, which "
                    "has no hook."),
        node(V, "hollow_spirit", "Hollow Spirit",
             "Your damaging spells leave the target taking 2% more damage per "
             "rank for three turns.",
             3, 2, 3, {}, connect=["hexplosion"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_hollow_spirit",
                       "name": "Hollow Spirit",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"damage_taken_pct": 0.02},
                       "on_target": True}},
             source="CoA: 'Damage dealt by Shadowflare and Hexfire now "
                    "increases the chance enemies are critically struck by 3% "
                    "for 12 seconds.' Crit-taken has no status hook on a "
                    "monster, so the debuff amplifies damage taken instead - "
                    "the same thing a higher crit rate is worth. Note "
                    "damage_taken_pct is the ONE status _pct key the engine "
                    "reads raw as a fraction."),
        node(V, "voodoo_mind", "Voodoo Mind",
             "Increases the damage of Shadow Puppets by 6% per rank.",
             3, 3, 3, {"ability_witch_doctor_shadow_puppets_damage": 0.06},
             connect=["jindos_wrath"],
             source="CoA: 'Shadow Puppets now ticks -10% faster and lasts 10% "
                    "longer for each Spirit active on you' - faster ticks over "
                    "a longer window is more total damage."),

        node(V, "dark_loas_blessing", "Dark Loa's Blessing",
             "Increases all damage you deal by 2% per rank.",
             4, 0, 3, {"all_damage": 0.02}, connect=["prolonged_malice"],
             total_slots=3,
             source="CoA: 'Increases the all damage dealt by party and raid "
                    "members by 3%.' GAP: a talent's effects only ever apply "
                    "to its owner - there is no party-wide talent aura - so "
                    "the party half is lost and the Witch Doctor keeps the "
                    "damage. This is one of the two nodes CoA points at when "
                    "it calls the spec an Augmentation Evoker."),
        node(V, "dark_effigy", "Dark Effigy",
             "Increases the damage your abilities deal to additional targets "
             "by 6% per rank.",
             4, 1, 3, {"aoe_damage": 0.06}, connect=["voodoo_strings"],
             total_slots=3,
             source="CoA: 'Your Bad Juju and Hexfire now strike 2 additional "
                    "nearby enemies.' Adding targets to a single-target spell "
                    "is not expressible, so the node makes the spec's existing "
                    "cleave hit harder instead."),
        node(V, "malicious_golems", "Malicious Golems",
             "Reduces the cooldown of War Golem by 1 turn and increases your "
             "haste by 1 per rank.",
             4, 2, 3, {"ability_witch_doctor_war_golem_cooldown": 1,
                       "haste": 1.0},
             connect=["hollow_spirit"], total_slots=3,
             source="CoA: 'Summoning your War Golem now increases your spell "
                    "haste by 30% for 20 seconds. In addition, periodic damage "
                    "dealt ... will reduce the cooldown of War Golem by -0.5 "
                    "sec.' Both halves, paid flat."),

        node(V, "de_other_side", "De Other Side",
             "Your damaging spells build power, granting 10 spell power and "
             "2% spell critical strike chance per rank for a short time.",
             5, 0, 2, {}, connect=["dark_loas_blessing"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_de_other_side",
                       "name": "De Other Side",
                       "effect_type": "buff",
                       "duration": 4,
                       "stat_mods": {"spell_power": 10,
                                     "crit_chance_spell": 2.0},
                       "on_target": False}},
             source="CoA: 'Damage dealt by Shadow Puppets now increases your "
                    "damage and critical strike chance by 1% for 20 seconds, "
                    "stacking up to 10 times.' The stack is the spec's engine "
                    "('Keep your De Other Side stacks alive off Shadow "
                    "Puppets so your damage stays high'); without a "
                    "stack-count field on a talent proc it is one refreshing "
                    "window instead of ten."),
        node(V, "the_price_of_power", "The Price of Power",
             "Increases your Spirit by 3% and grants spell damage equal to 2% "
             "of your Spirit per rank.",
             5, 1, 2, {"spirit_pct": 3.0, "spell_damage_from_spirit_pct": 0.02},
             connect=["dark_effigy"], total_slots=3,
             source="CoA: 'Voice of Bwonsamdi now increases your Spirit by "
                    "100%.' A cooldown-conditional doubling is not "
                    "expressible, so the node pays flat Spirit and doubles "
                    "down on the conversion that makes Spirit matter."),
        node(V, "juju_spirits", "Juju Spirits",
             "Increases your spell critical strike chance by 2% and your spell "
             "critical strike damage by 4% per rank.",
             5, 2, 2, {"crit_chance_spell": 2.0, "crit_damage_spell": 0.04},
             connect=["malicious_golems"], total_slots=3,
             source="CoA: 'Increases your spell critical damage by 100% and "
                    "increases the critical strike chance of Bad Juju by 5% "
                    "for each active Spirit on you.'"),

        node(V, "voice_of_bwonsamdi", "Voice of Bwonsamdi",
             "He has been waiting for you to ask.",
             6, 0, 1, {"shadow_spell_damage": 0.08, "crit_chance_spell": 4.0},
             node_type="active",
             connect=["de_other_side", "the_price_of_power", "juju_spirits"],
             total_slots=1,
             source="Capstone. CoA: 'Voice of Bwonsamdi is your big damage "
                    "cooldown', and the spec is rated PvE S with 'Strong "
                    "sustained single-target DPS on patchwork fights - high "
                    "throughput ceiling', so the payoff is throughput rather "
                    "than utility."),
    ],
    "Built from reference/coa_sidekick/SPEC_witch-doctor__voodoo.txt and the "
    "'voodoo' tree in reference/coa_sidekick/talents/witch-doctor.json. CoA "
    "calls it the Augmentation Evoker analog: 'fundamentally damage-dealers "
    "whose support value comes through buff and debuff windows and "
    "redirect-style cooldowns rather than sustained HPS ... Like "
    "Augmentation, it barely casts heals.' Nothing in this tree heals, "
    "deliberately - its stated weakness is 'No ally heal in the spec at all: "
    "no HoT, no direct heal, no off-heal filler.' Its stat priority is Spell "
    "Hit > SPIRIT > Spell Power > Haste > Crit > Intellect, which is why four "
    "nodes here spend on Spirit and two convert it into spell damage.")


# ================================================================= Brewing
B = "witch_doctor_brewing"
BREWING = tree(
    B, "Witch Doctor Brewing",
    "Healer. A throw-heal loop of Loa's Brew and Potion Toss over a Cauldron "
    "of Ingredients, Spices and Bases that spread mitigation across the "
    "party instead of spending it on one big button.",
    [
        node(B, "presence_of_the_loa", "Presence of the Loa",
             "Increases your spell critical strike chance by 1% per rank.",
             0, 0, 5, {"crit_chance_spell": 1.0},
             source="CoA: 'Increases your critical strike chance by 4%'. Crit "
                    "sits third in this spec's stat priority, above Haste."),
        node(B, "potent_mixes", "Potent Mixes",
             "Increases your healing power by 2% and reduces the threat your "
             "spells generate by 3% per rank.",
             0, 1, 5, {"healing_power_pct": 2.0,
                       "threat_generation_pct": -0.03},
             source="CoA: 'Increases your healing done by 4% and reduces the "
                    "threat generated by your spells by -15%' at 2 ranks. "
                    "healing_power_pct takes percentage POINTS here, so 2.0 is "
                    "+2% a rank - the opposite convention to the fractional "
                    "threat key beside it in the same dict."),
        node(B, "mojo_addiction", "Mojo Addiction",
             "Increases your maximum Mana by 2% per rank.",
             0, 2, 5, {"max_mana_pct": 0.02},
             source="CoA: 'Increases your maximum mana by 5%' at 2 ranks."),
        node(B, "plentiful_potions", "Plentiful Potions",
             "Reduces the Mana cost of your healing spells by 2% per rank.",
             0, 3, 5, {"heal_cost_pct": 0.02},
             source="CoA: 'Reduces the cost of your Loa's Brew and Hexbreak by "
                    "-10%'. NOTE the sign: talented_cost does cost * (1 - pct), "
                    "so a POSITIVE value is the discount. Authoring this "
                    "negative is the mistake that once made a whole spec's "
                    "heals more expensive than its tooltips promised."),

        node(B, "spirit_healer", "Spirit Healer",
             "Grants healing power equal to 3% of your Spirit per rank.",
             1, 0, 5, {"healing_power_from_spirit_pct": 0.03},
             connect=["presence_of_the_loa"],
             source="CoA: 'Increases healing power by 25% of Spirit and "
                    "increases spell critical strike chance by 10% of Spirit.' "
                    "Spirit is this spec's primary stat, so this is the node "
                    "the whole tree is built around. A real stat conversion."),
        node(B, "brewmaster", "Brewmaster",
             "Increases the healing of Loa's Brew by 4% per rank.",
             1, 1, 3, {"ability_witch_doctor_loas_brew_healing": 0.04},
             connect=["potent_mixes"],
             source="CoA: 'Reduces the cast time of Loa's Brew by 0.25 sec' at "
                    "2 ranks. Cast time does not exist in a turn engine, so "
                    "the node pays out as throughput on the same spell."),
        node(B, "potion_boss", "Potion Boss",
             "Increases the healing of Potion Toss by 5% per rank.",
             1, 2, 3, {"ability_witch_doctor_potion_toss_healing": 0.05},
             connect=["mojo_addiction"],
             source="CoA: 'Increases the effectiveness of Potion Toss and your "
                    "tossed Ingredients by 20%.'"),
        node(B, "mixologist", "Mixologist",
             "Increases your Spirit by 2% per rank.",
             1, 3, 5, {"spirit_pct": 2.0}, connect=["plentiful_potions"],
             source="CoA ships Mixologist with no tooltip at all ('see builder "
                    "tooltip'). Placed as the Spirit node its name and its "
                    "no-gate slot imply, which is also what Spirit Healer "
                    "above needs to be worth taking."),

        node(B, "disciple_of_sseratus", "Disciple of Sseratus",
             "Increases all healing you do by 3% per rank.",
             2, 0, 3, {"healing_done": 0.03}, connect=["spirit_healer"],
             source="CoA: 'Increases the bonus healing scaling of Loa's Brew "
                    "and Spirit in a Bottle by 15%.'"),
        node(B, "fresh_ingredients", "Fresh Ingredients",
             "Increases the healing of Ingredient: Jungle Shrooms by 4% per "
             "rank.",
             2, 1, 5, {"ability_witch_doctor_ingredient_jungle_shrooms_healing": 0.04},
             connect=["brewmaster"],
             source="CoA: 'Increases the healing of your Jungle Shrooms from "
                    "your Cauldron by 15%' at 2 ranks."),
        node(B, "splash_on_em", "Splash On 'Em",
             "Reduces the cooldown of Potion Toss by 1 turn per rank.",
             2, 2, 2, {"ability_witch_doctor_potion_toss_cooldown": 1},
             connect=["potion_boss"],
             source="CoA: 'Effective healing done by Loa's Brew and Mojo Beam "
                    "reduce the cooldown of Potion Toss and Splash Potion by "
                    "-1 sec.' A heal-driven cooldown chip has no hook, so it is "
                    "a flat reduction - which is why Potion Toss ships on a "
                    "3-turn cooldown rather than 1."),
        node(B, "senjins_presence", "Sen'jin's Presence",
             "Reduces the Mana cost of your healing spells by 2% per rank.",
             2, 3, 4, {"healing_spell_cost_pct": 0.02},
             connect=["mixologist"],
             source="CoA: 'Casting Potion Toss and Spirit in a Bottle now "
                    "reduce the cast time of your next 2 Loa's Brews by -20%'. "
                    "A conditional cast-time cut becomes a flat cost cut - the "
                    "resource the turn engine actually charges you."),

        node(B, "jungle_secrets", "Jungle Secrets",
             "Your heals spill 10% of their value onto your other allies, per "
             "rank.",
             3, 0, 3, {}, connect=["disciple_of_sseratus"],
             proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
                   "splash_heal": {"pct": 0.10}},
             source="CoA: 'When you heal with Loa's Brew your Effigies will "
                    "now heal an additional ally within 20 yds for 35% of the "
                    "healing done, prioritizing allies with low health.' "
                    "splash_heal is the engine's own spread-a-fraction-of-this-"
                    "heal payload."),
        node(B, "doctor_of_the_jungle", "Doctor of the Jungle",
             "Increases the healing of Mojo Beam by 5% per rank.",
             3, 1, 3, {"ability_witch_doctor_mojo_beam_healing": 0.05},
             connect=["fresh_ingredients"],
             source="CoA: 'Jungle Shrooms used from your Cauldron now ticks -3 "
                    "sec faster' and 'Jungle Booms ... ticks -0.5 sec faster' - "
                    "faster ticks are more healing per window, and Mojo Beam is "
                    "the channel they are tuned around."),
        node(B, "spice_earthroot", "Spice: Earthroot",
             "Grants 5 healing power and 3 Spirit per rank.",
             3, 2, 3, {"healing_power": 5, "spirit": 3},
             connect=["splash_on_em"],
             source="CoA: 'Infuse your Cauldron with Spice: Earthbloom. "
                    "Increases effectiveness of all Cauldron effects and "
                    "Ingredients by 30%.' A multiplier on a category of "
                    "abilities has no key, so the Spice pays flat healing "
                    "power - and Spirit, which this spec converts into more."),
        node(B, "spice_peacebloom", "Spice: Peacebloom",
             "Reduces the duration of stuns used against you by 10% per rank.",
             3, 3, 2, {"stun_duration_reduction_pct": 0.10},
             connect=["senjins_presence"],
             source="CoA: 'Reduces the duration of roots, stuns, and snares "
                    "against allies within 40 yds by -25%.' The stun half is a "
                    "real key, read in StatusEffectMixin; it applies to you "
                    "only, because stun_duration_reduction_pct is read through "
                    "get_talent_effect and a talent has no party reach."),

        node(B, "touch_of_the_spirits", "Touch of the Spirits",
             "Your damaging spells leave the target taking 2% more damage and "
             "dealing 4% less, per rank.",
             4, 0, 3, {}, connect=["jungle_secrets"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_touch_of_the_spirits",
                       "name": "Touch of the Spirits",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"damage_taken_pct": 0.02,
                                     "damage_dealt_pct": -4},
                       "on_target": True}},
             source="CoA: 'Damage dealt by Spirit In a Bottle causes the "
                    "enemies to take 3% more damage and deal -3% less damage "
                    "for 15 seconds.' This is the node CoA means by 'you "
                    "pressure while you protect'. The two keys take DIFFERENT "
                    "units inside a status effect: damage_taken_pct raw, "
                    "damage_dealt_pct in percentage points."),
        node(B, "its_da_mojo", "It's Da Mojo",
             "Increases your spell critical strike chance by 1% and your spell "
             "critical strike damage by 4% per rank.",
             4, 1, 3, {"crit_chance_spell": 1.0, "crit_damage_spell": 0.04},
             connect=["doctor_of_the_jungle"], total_slots=3,
             source="CoA: 'Allows your Mojo Beam to critically heal.' A "
                    "per-ability crit permission has no flag, so the node "
                    "carries the crit it was granting access to."),
        node(B, "master_of_concoctions", "Master of Concoctions",
             "Your Ingredients last 1 turn longer per rank.",
             4, 2, 2, {"ability_witch_doctor_ingredient_jungle_shrooms_duration": 1,
                       "ability_witch_doctor_ingredient_frog_bones_duration": 1,
                       "ability_witch_doctor_ingredient_bloodthistle_duration": 1},
             connect=["spice_earthroot"], total_slots=3,
             source="CoA: 'Increases the duration of Ingredients by 20% and "
                    "causes allies affected by Jungle Shrooms to heal for 5% "
                    "of the damage they deal.' The duration half covers all "
                    "three Ingredients; the leech half is already Bloodthistle's "
                    "own proc and is not paid twice."),

        node(B, "mojo_wave", "Mojo Wave",
             "Your heals spill a further 12% of their value onto your other "
             "allies, per rank.",
             5, 0, 2, {}, connect=["touch_of_the_spirits"], total_slots=3,
             proc={"trigger": "on_heal_cast", "chance": 100, "icd": 0,
                   "splash_heal": {"pct": 0.12}},
             source="CoA: 'Healing with Mojo Beam now heals up to 3 of the "
                    "lowest health nearby allies within 20 yds for 75% of the "
                    "healing done.' Stacks with Jungle Secrets, which is how "
                    "CoA's own free passives stack with its picks."),
        node(B, "unstable_concoction", "Unstable Concoction",
             "Increases the healing you do to allies below 35% health by 3% "
             "per rank.",
             5, 1, 2, {"low_health_healing_pct": 0.03,
                       "low_health_threshold_pct": 0.35},
             connect=["its_da_mojo"], total_slots=3,
             source="CoA: 'Potion Toss now applies Unstable Concoction ... "
                    "Using Loa's Brew or Spirit in a Bottle on the target will "
                    "trigger an explosion of mojo around the target, healing "
                    "nearby allies'. A two-cast combo is not expressible, so "
                    "the node becomes the emergency throughput it was for. "
                    "low_health_healing_pct is read recipient-side in the heal "
                    "path."),
        node(B, "loas_blessing", "Loa's Blessing",
             "Your heals leave the target receiving 8% more healing per rank "
             "for three turns.",
             5, 2, 2, {}, connect=["master_of_concoctions"], total_slots=3,
             proc={"trigger": "on_heal_cast", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_loas_blessing",
                       "name": "Loa's Blessing",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"healing_taken_pct": 8},
                       "on_target": True}},
             source="CoA: 'Healing done by Loa's Brew now applies a random "
                    "empowerment to the target ally.' A random pick from a "
                    "table is not something a proc can express, so the "
                    "empowerment is the one that always helps a healer: the "
                    "next heal lands harder."),

        node(B, "master_mixologist", "Master Mixologist",
             "You stop measuring.",
             6, 0, 1, {"healing_done": 0.10, "healing_power_pct": 4.0},
             node_type="active",
             connect=["mojo_wave", "unstable_concoction", "loas_blessing"],
             total_slots=1,
             source="Capstone. CoA: 'Master Mixologist is the big amplify "
                    "window', held 'as the group heal-burst and "
                    "wipe-prevention amplify window for a burst mechanic the "
                    "group needs to survive'. The spec is rated Dun B / Raid C "
                    "with a 'moderate throughput ceiling', so the capstone "
                    "raises the ceiling rather than adding another button."),
    ],
    "Built from reference/coa_sidekick/SPEC_witch-doctor__brewing.txt and the "
    "'brewing' tree in reference/coa_sidekick/talents/witch-doctor.json. CoA: "
    "'Closest to Preservation Evoker, mechanically rather than by vibe ... Its "
    "group mitigation is distributed across the Cauldron Bases and "
    "Ingredients ... That parallels Preservation's spread-the-mitigation "
    "approach rather than one big raid button.' Stat priority is SPIRIT > "
    "Spell Power > Crit > Haste > Intellect, so Spirit Healer and Mixologist "
    "carry the tree the way Spell Power usually would. The one thing this "
    "spec genuinely lacks in CoA and lacks here too is hard single-target CC: "
    "'Where it diverges from Evoker is hard single-target CC, of which it has "
    "none of its own.'")


# =========================================================== Shadowhunting
S = "witch_doctor_shadowhunting"
SHADOWHUNTING = tree(
    S, "Witch Doctor Shadowhunting",
    "Ranged weapon and Serpent Wards. Banks Spirit off Reclamation into "
    "Spirit Eclipse, shuts a target off with Spirit Shock and Hex of Death, "
    "and carries party auras on a shamanic chassis.",
    [
        node(S, "loas_strength", "Loa's Strength",
             "Increases your Agility by 2% and the Nature and Shadow damage "
             "you deal by 2% per rank.",
             0, 0, 5, {"agility_pct": 2.0, "nature_shadow_damage_pct": 0.02},
             source="CoA: 'Increases your Agility and your Nature and Shadow "
                    "damage dealt by 3%' at 2 ranks. nature_shadow_damage_pct "
                    "is a combined school key - the engine resolves it per "
                    "underscore component against the real school set, so it "
                    "covers both."),
        node(S, "improved_malefic_arrow", "Improved Malefic Arrow",
             "Increases the damage of Malefic Arrow by 5% per rank.",
             0, 1, 5, {"ability_witch_doctor_malefic_arrow_damage": 0.05},
             source="CoA: 'Reduces the cooldown of Malefic Arrow by -2 sec' at "
                    "2 ranks. Malefic Arrow is already on a 2-turn cooldown "
                    "here, which a flat reduction would erase entirely, so the "
                    "node pays throughput instead."),
        node(S, "village_wisdom", "Village Wisdom",
             "Increases your hit chance by 1% and the damage of Reclamation by "
             "4% per rank.",
             0, 2, 5, {"hit_rating": 1,
                       "ability_witch_doctor_reclamation_damage": 0.04},
             source="CoA: 'Increases your hit chance by 5% and the damage of "
                    "Reclamation by 15%.' Both halves, per rank."),
        node(S, "shadowhunter", "Shadowhunter",
             "Reduces the Mana cost of all your abilities by 2% per rank.",
             0, 3, 5, {"all_ability_cost_pct": 0.02},
             source="CoA: 'Allows you to auto shoot with a ranged weapon. In "
                    "addition, reduces the mana cost of all spells and "
                    "abilities by -25%.' Auto-shoot already exists for every "
                    "class through data/abilities/_universal.json, so the cost "
                    "cut is the live half. POSITIVE is the discount here - "
                    "talented_cost does cost * (1 - pct)."),

        node(S, "senjins_apprentice", "Sen'jin's Apprentice",
             "Grants ranged attack power equal to 2% of your Intellect and "
             "spell damage equal to 2% of your Agility, per rank.",
             1, 0, 5, {"ranged_ap_from_intellect_pct": 0.02,
                       "spell_damage_from_agility_pct": 0.02},
             connect=["loas_strength"],
             source="CoA: 'Increases your ranged attack power by 100% of your "
                    "Intellect and your ranged attack power and spell power by "
                    "25% of your Agility.' Two real stat conversions, and the "
                    "reason CoA says 'your shots scale off both'."),
        node(S, "spiritual_devotee", "Spiritual Devotee",
             "Increases your maximum Mana by 2% and restores 2 Mana every 5 "
             "seconds, per rank.",
             1, 1, 3, {"max_mana_pct": 0.02, "mp5": 2},
             connect=["improved_malefic_arrow"],
             source="CoA: 'Collecting a Spirit now instantly restores 3% of "
                    "your maximum mana.' Spirits are not a resource here (see "
                    "the module docstring), so the refund becomes a real pool "
                    "and a real regen rate."),
        node(S, "shadow_enchantments", "Shadow Enchantments",
             "Increases the damage of Hex of Malice by 5% per rank.",
             1, 2, 3, {"ability_witch_doctor_hex_of_malice_damage": 0.05},
             connect=["village_wisdom"],
             source="CoA: 'Increases the duration and effectiveness of your "
                    "Jinxes by 25%' at 2 ranks. Hex of Malice is the Jinx this "
                    "spec actually keeps rolling."),
        node(S, "eye_of_kimbul", "Eye of Kimbul",
             "Increases your critical strike chance by 1% per rank, with both "
             "weapons and spells.",
             1, 3, 5, {"crit_chance_physical": 1.0, "crit_chance_spell": 1.0},
             connect=["shadowhunter"],
             source="CoA: 'Critical strikes now apply Eye of Kimbul to "
                    "enemies. Increases damage dealt and critical strike chance "
                    "against this target by 1%, stacking 5 times.' Crit is "
                    "second in this spec's stat priority and its damage is "
                    "split between ranged weapon and spells, so the node "
                    "covers both."),

        node(S, "spirit_hunting", "Spirit Hunting",
             "Your damaging abilities have a 25% chance to restore 20 Mana, "
             "per rank.",
             2, 0, 3, {}, connect=["senjins_apprentice"],
             proc={"trigger": "on_damage_cast", "chance": 25, "icd": 1,
                   "grant_resource": {"resource": "mana", "amount": 20}},
             source="CoA: 'Each active Spirit gives you a 15% chance when you "
                    "cast Malefic Arrow to generate an additional Spirit.' A "
                    "Spirit is health and Mana back, so the proc grants Mana."),
        node(S, "berserking", "Berserking",
             "Increases your haste by 1 per rank.",
             2, 1, 5, {"haste": 1.0}, connect=["spiritual_devotee"],
             source="CoA: 'Periodic damage dealt now has a 25% chance to "
                    "increase the haste of your Serpent Wards by 3% for 15 "
                    "seconds, stacking up to 3 times.' Wards are not separate "
                    "actors here, so the haste is yours."),
        node(S, "godslayer", "Godslayer",
             "Increases the damage of Spirit Glaive by 6% per rank.",
             2, 2, 3, {"ability_witch_doctor_spirit_glaive_damage": 0.06},
             connect=["shadow_enchantments"],
             source="CoA: 'Your Spirit Glaive now deals an additional shadow "
                    "damage to up to 5 nearby enemies at the end of its "
                    "duration.'"),
        node(S, "hex_of_death", "Hex of Death",
             "Your damaging abilities cut the healing the target receives by "
             "6% per rank for three turns.",
             2, 3, 3, {}, connect=["eye_of_kimbul"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "apply_effect": {
                       "effect_id": "witch_doctor_hex_of_death",
                       "name": "Hex of Death",
                       "effect_type": "debuff",
                       "duration": 3,
                       "stat_mods": {"healing_taken_pct": -6},
                       "on_target": True}},
             source="CoA: 'Damage dealt by Malefic Arrow now reduces the "
                    "targets healing received by -20% for 10 seconds, stacking "
                    "2 times'; 'Hex of Death cuts a target's healing received "
                    "via Malefic Arrow. You shut a target off, not just damage "
                    "it.' healing_taken_pct inside a status effect takes "
                    "percentage POINTS."),

        node(S, "the_true_spirit", "The True Spirit",
             "Increases the damage of Spirit Eclipse by 6% per rank.",
             3, 0, 3, {"ability_witch_doctor_spirit_eclipse_damage": 0.06},
             connect=["spirit_hunting"],
             source="CoA: 'Summoning a Serpent Ward or Spirit now increases "
                    "the damage of your next Spirit Glaive or Spirit Eclipse "
                    "by 6% for 10 seconds, stacking 5 times.' The stacking "
                    "condition has no hook; the 6% is real."),
        node(S, "serpents_guile", "Serpent's Guile",
             "Increases the damage of your Nature damage-over-time effects by "
             "3% per rank.",
             3, 1, 3, {"nature_dot_damage": 0.03}, connect=["berserking"],
             source="CoA: 'Your Malefic Arrow now deals an additional 15% of "
                    "its damage dealt every 1 sec for 4 seconds as Nature "
                    "damage.' Adding a DoT to a direct-damage ability is not "
                    "expressible, so the node scales the Nature DoTs the spec "
                    "already has - Call of Sseratus above all."),
        node(S, "voodoo_fire", "Voodoo Fire",
             "Increases the damage of Call of Sseratus by 6% per rank.",
             3, 2, 3, {"ability_witch_doctor_call_of_sseratus_damage": 0.06},
             connect=["godslayer"],
             source="CoA: 'Your Serpent Ward's attacks now have a 20% chance "
                    "to shoot Voodoo Fire, dealing Fire damage to up to 3 "
                    "nearby enemies' at 2 ranks, plus 'Spirit Striker - "
                    "Increases the proc chance of Voodoo Fire by 10%.' Two "
                    "nodes' worth of ward damage, folded into one."),
        node(S, "umbral_glaive", "Umbral Glaive",
             "Reduces the cooldown of Spirit Glaive by 1 turn per rank.",
             3, 3, 2, {"ability_witch_doctor_spirit_glaive_cooldown": 1},
             connect=["hex_of_death"],
             source="CoA ships Umbral Glaive with no tooltip ('see builder "
                    "tooltip'), but the rotation says what it does: 'Keep Hex "
                    "of Malice rolling with Umbral Glaive. Its glaive refreshes "
                    "Hex of Malice's duration and leeches health, so you re-up "
                    "the dot without re-casting it.' A refresh-on-hit has no "
                    "hook, so more glaives is the honest version."),

        node(S, "strength_of_da_loa", "Strength of Da Loa",
             "Increases your attack power by 3% per rank.",
             4, 0, 3, {"attack_power_pct": 3.0}, connect=["the_true_spirit"],
             total_slots=3,
             source="CoA: 'Increases the attack power of party and raid "
                    "members by 5%.' GAP: a talent reaches its owner only, so "
                    "the party half is lost. Attack power still matters here - "
                    "it leads this spec's stat priority, ahead of Agility."),
        node(S, "darkspear_traditionalist", "Darkspear Traditionalist",
             "Increases your haste by 1 and all damage you deal by 2% per "
             "rank.",
             4, 1, 3, {"haste": 1.0, "all_damage": 0.02},
             connect=["serpents_guile"], total_slots=3,
             source="CoA: 'Emanate a powerful aura, granting 10% increased "
                    "melee and ranged haste to party and raid members.' Same "
                    "party-reach gap as Strength of Da Loa above."),
        node(S, "bwonsamdis_edge", "Bwonsamdi's Edge",
             "Increases the damage your abilities deal to additional targets "
             "by 6% per rank.",
             4, 2, 3, {"aoe_damage": 0.06}, connect=["voodoo_fire"],
             total_slots=3,
             source="CoA: 'Your Spirit Eclipse now deals 40% increased damage "
                    "when it explodes on impact' - the explosion is what hits "
                    "the enemies around the target."),

        node(S, "dambalas_lethality", "Dambala's Lethality",
             "Increases your critical strike damage by 4% per rank, with both "
             "weapons and spells.",
             5, 0, 2, {"crit_damage_physical": 0.04, "crit_damage_spell": 0.04},
             connect=["strength_of_da_loa"], total_slots=3,
             source="CoA: 'After using Spirit Eclipse, the damage of your next "
                    "Shadowflare within 15 seconds is increased by 50%.' A "
                    "one-cast window off another cast has no hook, so the node "
                    "becomes burst of the kind the spec can actually keep - "
                    "crit damage, on both of its damage types."),
        node(S, "a_price_to_pay", "A Price To Pay",
             "Your critical strikes have a 30% chance to reset the cooldown of "
             "Spirit Glaive, per rank.",
             5, 1, 2, {}, connect=["darkspear_traditionalist"], total_slots=3,
             proc={"trigger": "on_crit", "chance": 30, "icd": 1,
                   "reset_cooldown": {"ability": "witch_doctor_spirit_glaive"}},
             source="CoA: 'Casting Spirit Eclipse with 5 Spirits now resets the "
                    "cooldown of Spirit Glaive and causes your next cast within "
                    "8 seconds to be guaranteed to critically strike.' "
                    "reset_cooldown is a real proc payload, so the reset half "
                    "is literal; the guaranteed crit is not expressible, so the "
                    "proc fires off crits instead of granting one."),
        node(S, "viper_ward", "Viper Ward",
             "Increases the Fire damage you deal by 3% per rank.",
             5, 2, 2, {"fire_spell_damage": 0.03},
             connect=["bwonsamdis_edge"], total_slots=3,
             source="CoA: 'Transforms Call of Sseratus into Viper Ward ... "
                    "Viper Wards have a 50% chance to unleash a Hexfire Blast, "
                    "dealing Fire damage to an enemy.' Replacing one ability "
                    "with another needs an unlock_ability and a second ward "
                    "spell; the Fire damage the transformation is for is the "
                    "honest single-node version."),

        node(S, "frenzied_spirits", "Frenzied Spirits",
             "You spend every spirit you were carrying at once.",
             6, 0, 1, {"crit_chance_physical": 4.0, "crit_chance_spell": 4.0,
                       "crit_damage_physical": 0.08},
             node_type="active",
             connect=["dambalas_lethality", "a_price_to_pay", "viper_ward"],
             total_slots=1,
             source="Capstone. CoA: 'Consumes your Spirits to increase your "
                    "ranged critical strike rating by 10, critical damage by "
                    "5%, and causing you to heal for 2% of all damage dealt "
                    "for each Spirit consumed.' The leech half is already on "
                    "the ability of the same name, so the talent carries the "
                    "crit."),
    ],
    "Built from reference/coa_sidekick/SPEC_witch-doctor__shadowhunting.txt "
    "and the 'shadowhunting' tree in reference/coa_sidekick/talents/"
    "witch-doctor.json. CoA: 'Closest to a Survival Hunter built on a shamanic "
    "support chassis ... Mechanically it's a support-flavored chassis that was "
    "talented into being a real ranged-hybrid combatant, spending most of its "
    "buttons on Spirit-fueled ranged damage rather than on healing.' Its stat "
    "priority is Attack Power > Crit > Agility > Intellect/Spirit > Spell "
    "Power, which is why this is the one Witch Doctor tree that spends on "
    "attack power and physical crit at all, and why Sen'jin's Apprentice - "
    "which pays Intellect into ranged attack power and Agility into spell "
    "damage - is its keystone. Its stated weakness is CC: 'Shadowstalker "
    "wipes harmful effects on its own timer and that is the entire answer to "
    "CC', and nothing in this tree pretends otherwise.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Witch Doctor",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/witch_doctor.json", ability_doc),
        (ROOT / "data/talents/witch_doctor_voodoo.json", VOODOO),
        (ROOT / "data/talents/witch_doctor_brewing.json", BREWING),
        (ROOT / "data/talents/witch_doctor_shadowhunting.json", SHADOWHUNTING),
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
