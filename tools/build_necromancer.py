#!/usr/bin/env python3
"""Author the Necromancer: ability kit + three talent trees.

    PYTHONPATH=. python3 tools/build_necromancer.py [--apply]

Necromancer is one of the twelve CoA classes that had base stats, cloth
armour, a weapon list and a resource but no abilities and no talents, so it
could not be selected. CoA calls it "a form of mage specialising in the dark
arts ... they spread terrible plagues, conjure icy magic, and summon legions
of undead", and the three specs split exactly along those three lines:

  Death      RANGED DPS  "Closest to Unholy/Blood Death Knight, with an
                         Affliction Warlock veneer." Pure disease
                         throughput - stack diseases, then amplify them.
  Rime       RANGED DPS  "Closest to a Frost Death Knight reskinned as a
                         pure ranged caster with an Unholy DK pet layer
                         bolted on." Freeze, then detonate.
  Animation  RANGED DPS  "Closest to Unholy Death Knight for the mechanical
                         shell: a Runic Power economy, a plague layer, and a
                         rotating army of pets." You play less like a
                         spellcaster and more like a one-person raid group.

SOURCE. reference/coa_sidekick/CLASS_necromancer.txt, the three
SPEC_necromancer__*.txt pages and reference/coa_sidekick/talents/
necromancer.json (38 class-tree nodes, 39/41/42 spec nodes), all captured
from ascensionsidekick.com. Every ability and talent name below is a real CoA
name off those pages; nothing is invented to fill a slot. CoA's trees are
~40 nodes behind three point gates, Frontier's are ~23 behind seven tiers, so
this selects the nodes that actually carry each spec rather than
transcribing - see that reference's own README for the shape difference.

NUMBERS ARE FRONTIER'S, NOT CoA'S. The reference is a fan-made planning tool
whose own disclaimer says COA is pre-meta. Damage curves copy the two shipped
cloth casters: warlock_shadow_bolt / mage_frostbolt for direct nukes (9 ranks
at levels 1/6/12/18/24/32/40/48/56, base ~42, +11 a rank) and
warlock_corruption / warlock_immolate for DoTs (base ~95, +30 a rank over a
4-turn duration), because the Necromancer should scale alongside them rather
than on a curve of its own invention.

LIFE FORCE, AND THE ONE REAL PROBLEM WITH IT. CLASS_RESOURCE_MAP gives
Necromancer ResourceType.LIFE_FORCE and no secondary. Life Force is
dict-backed (it is not in Character._RESOURCE_ATTRS), so it caps at
SECONDARY_RESOURCE_MAX = 100 and costs must be FLAT across ranks. More
importantly: NOTHING IN THE ENGINE REGENERATES IT. A Necromancer is created
with secondary_resources = {} - Life Force 0 - and neither
restore_resources_between_turns (Energy and Mana only) nor
restore_resources_out_of_combat_step (Energy, and Rage decay) ever adds any.
A class whose every ability cost Life Force would therefore be permanently
uncastable.

So the kit is a builder/spender, which is also what CoA describes: in CoA,
Crypt Swarm, Lichfrost and Flesh to Worms GENERATE Runic Power and the
"Command" spells SPEND it. Here:

  builders   cost 0 and carry `generates` {"resource": "life_force", ...} -
             Crypt Swarm 20, Flesh to Worms 15, Lichfrost 12
  spenders   cost a flat 15 to 40, sized against a builder cast or two
  Glacial Tap  restores 30 Life Force outright, CoA's own relief valve
             ("instantly regenerating 30 Runic Power")

This is the same shape Stormbringer's Mana->Static and Cultist's
Mana->Insanity already ship with, with one difference forced by the engine:
those classes pay for their builders in Mana, and a Necromancer has no Mana
at all (_recalculate_derived_stats only gives a Mana pool to Mana-resource
classes, so self.mana is 0), which is why the builders here are free rather
than Mana-priced.

TALENT EFFECT KEYS are restricted to ones the engine actually reads, verified
with tools/validate_class.py. Casualties worth recording:

  life_force_max  WOULD work - Character.get_resource_max reads
                  f"{key}_max" generically off the resource key, which is
                  the whole point of that method - but
                  tools/audit_talents.py's _NAMED_LIVE hardcodes the five
                  pools that existed when it was written (static_max,
                  energy_max, insanity_max, runes_max, solar_power_max) and
                  so reports life_force_max dead. Three CoA talents are
                  about exactly this pool (Ner'zhul's Blessing, Runic
                  Reservoir, Summoning Adept/Expert/Prodigy, Master
                  Animator). They carry pet durability, cost reduction or
                  Frost damage instead, each noted at its node.
  ally-facing     A talent only ever reads off its OWN character
                  (get_talent_effect), so CoA's party auras (Icecrown,
                  Chilling Presence, Corpse Wagon, Apothecary's Cauldron)
                  cannot be talents here. Each is an ABILITY with
                  buff_scope "party" instead, and the talent of the same
                  name carries only its self-facing half.
  enemy debuffs   Monster reads exactly two stat_mods off its status
                  effects - armor and attack_power (see Monster.armor /
                  Monster.ability_power_bonus). magic_damage_taken_pct on
                  an enemy does nothing against a monster, so Expunge and
                  Master Lich are expressed on the caster's own side.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Warlock's and Mage's shipped rank schedule - see module docstring.
RANK_LEVELS = [1, 6, 12, 18, 24, 32, 40, 48, 56]


def ranks(base, step, cost, start=1, count=9, **rank_extra):
    """Flat-cost rank table on the shipped caster schedule, from `start`.

    Costs are FLAT, not scaled, because Life Force is a 0-100 pool rather
    than a Mana bar: Mage's 25->85 Frostbolt curve would make rank 9 of
    anything a third of the whole pool. Levels past the 9-rank schedule are
    spaced evenly to stay under 58 so every rank is reachable at the level
    60 cap.
    """
    if start == 1:
        levels = RANK_LEVELS[:count]
    else:
        span = max(1, (58 - start) // max(1, count - 1)) if count > 1 else 1
        levels = [min(58, start + i * span) for i in range(count)]
    return [{"rank": i + 1, "level_req": lv, "cost": cost,
             "effect_value": int(round(base + step * i)), **rank_extra}
            for i, lv in enumerate(levels)]


def one(level, cost, value=0, **rank_extra):
    """Single-rank table, for cooldowns and stances that do not scale."""
    return [{"rank": 1, "level_req": level, "cost": cost,
             "effect_value": value, **rank_extra}]


def ability(aid, name, effect_type, description, rank_table, *, cooldown=0,
            duration=0, stat_mods=None, icon=None, source=None, **extra):
    """One ability. `icon` defaults to None - no art exists for an invented
    icon id, and the Necromancer is a pure caster, so only the conventional
    free Attack carries "ability_melee"."""
    out = {
        "ability_id": f"necromancer_{aid}",
        "name": name,
        "resource_type": "life_force",
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


def generates(amount):
    """`generates` payload for a Life Force builder."""
    return {"resource": "life_force", "amount": amount}


# ============================================================== ability kit
# Order is roughly the order a player meets them.
ABILITIES = [
    ability("attack", "Attack", "damage",
            "A swing with whatever you are holding.", one(1, 0, 0),
            icon="ability_melee",
            source="Convention: every class ships a free rank-1 Attack. The "
                   "only weapon strike a Necromancer has, hence the only "
                   "ability_melee icon in the file."),

    # ---- the Life Force economy, all three specs
    ability("crypt_swarm", "Crypt Swarm", "spell_damage",
            "A swarm of carrion insects pours off you and settles on the "
            "target. It does not hurry.",
            ranks(34, 9, 0), target_type="enemy", damage_school="shadow",
            generates=generates(20),
            source="CoA: 'Pull with Crypt Swarm, a channel that builds RP "
                   "while ticking Plague damage'. The engine of all three "
                   "rotations, so it is the level-1 free builder and the "
                   "biggest Life Force source in the kit. Deliberately "
                   "weaker per cast than Lichfrost - you are paid in fuel."),
    ability("lichfrost", "Lichfrost", "spell_damage",
            "A lance of grave-cold that leaves the target slow and stiff.",
            ranks(44, 11, 0), target_type="enemy", damage_school="frost",
            generates=generates(12),
            source="CoA: 'Open at range with Lichfrost (builder, generates "
                   "Runic Power, slows)'. Shared by all three specs - the "
                   "class tree spends points on it (Lich Essence, Living "
                   "Dead, Winds of Northrend). mage_frostbolt's curve. The "
                   "slow is not modelled: a haste debuff on an enemy is read "
                   "by nothing in Monster, which only folds armor and "
                   "attack_power off its status effects."),
    ability("flesh_to_worms", "Flesh to Worms", "spell_dot",
            "The target's flesh starts moving on its own.",
            ranks(88, 28, 0, start=4, count=8), duration=4,
            target_type="enemy", damage_school="shadow",
            generates=generates(15),
            source="CoA: 'Disease an enemy, dealing shadow SP Plague damage "
                   "and generating Runic Power every 3 sec for 18 seconds'. "
                   "warlock_corruption's DoT curve. Plague is not a school "
                   "here, and CoA's own wording is 'shadow SP Plague "
                   "damage', so every disease in this file is Shadow."),
    ability("glacial_tap", "Glacial Tap", "restore_resource",
            "You take what the dead are no longer using.",
            one(10, 0, 0, mana_restore_pct=30), cooldown=6,
            target_type="self", restore_resource_type="life_force",
            is_instant=True,
            source="CoA class tree: 'Tap into necrotic energies, instantly "
                   "regenerating 30 Runic Power'. Life Force has no engine "
                   "regen at all (see module docstring), so this is the only "
                   "way to refill the pool without casting a builder. "
                   "mana_restore_pct is the existing rank field for 'percent "
                   "of max resource restored' - 30 of a 100 pool is 30."),

    # ---- Command spells: the Life Force spenders every spec shares
    ability("command_hook", "Command: Hook", "debuff",
            "A hook comes out of the dark and the target stops going "
            "anywhere.",
            one(12, 15), cooldown=4, duration=1, target_type="enemy",
            is_stun=True, is_instant=True,
            source="CoA class tree: 'Command your Abominations to hook an "
                   "enemy to their location, slowing their movement speed to "
                   "a halt for 2 seconds'. A halt is a root; the engine has "
                   "no root, so it lands as a one-turn stun."),
    ability("corpse_explosion", "Corpse Explosion", "spell_damage",
            "You find a body nobody was watching and burst it.",
            ranks(46, 13, 25, start=16, count=7), cooldown=2,
            target_type="enemy_aoe", max_targets=4, damage_school="shadow",
            source="CoA class tree spends a point on it (Corpse Commander: "
                   "'Reduces the Runic Power cost of Corpse Explosion by "
                   "-20'), so it is baseline kit. enemy_aoe, not is_aoe: "
                   "target_type is the only field the engine's AoE branch "
                   "reads, and max_targets caps the cleave at 4."),
    ability("deaths_due", "Death's Due", "dispel",
            "You remind the target what it is owed.",
            one(26, 20), cooldown=6, target_type="enemy", dispel_type="magic",
            source="CoA: 'Force a target to accept the reality of death, "
                   "removing any invulnerability or immunity effects from "
                   "them'. An enemy purge - the same shape as shaman_purge "
                   "and stormbringer_razorwind. The 5-second curse and its "
                   "below-20% payoff have no hook and are dropped."),

    # ---- defence and utility, all three specs
    ability("bone_tithe", "Bone Tithe", "buff",
            "You take back some of what you lent your servants.",
            ranks(110, 40, 20, start=14, count=4), cooldown=5, duration=3,
            stat_mods={"armor": 120, "magic_resistance": 55},
            target_type="self", buff_scope="combat", is_instant=True,
            source="CoA class tree: 'Siphon life from your undead minions, "
                   "sacrificing 40% of their health to grant yourself an "
                   "absorb shield ... Usable while stunned'. There is no "
                   "absorb-shield mechanic, so it is an armour and magic "
                   "resistance window, the same substitution "
                   "mage_ice_barrier and priest_power_word_shield already "
                   "ship with. Nothing models 'usable while stunned'."),
    ability("fetid_ward", "Fetid Ward", "buff",
            "A sweet, thick smell settles over you and everything you have "
            "raised.",
            one(18, 25), cooldown=6, duration=5,
            stat_mods={"healing_power": 45, "magic_resistance": 40},
            target_type="self", buff_scope="combat",
            source="CoA class tree: 'While active, 30% of your damage dealt "
                   "heals you and your minions ... and healing received is "
                   "increased by 10%'. Damage-to-healing conversion has no "
                   "ability-level hook, so the healing-received half is what "
                   "the buff carries. Animation's Vampiric Aura talent is "
                   "where the leech actually lives."),
    ability("anti_magic_shell", "Anti-Magic Shell", "buff",
            "Spellwork slides off you and off everything standing near you.",
            one(38, 25), cooldown=8, duration=3,
            stat_mods={"magic_damage_taken_pct": -25},
            target_type="self", buff_scope="combat", is_instant=True,
            source="CoA: 'Anti-Magic Shell raises every summon with a "
                   "magic-absorb bubble'. NOTE the convention trap: "
                   "magic_damage_taken_pct from a BUFF is percent POINTS "
                   "(divided by 100 in Character.take_damage) while the "
                   "TALENT form of the same key is a fraction. -25 is -25%."),
    ability("phylactery", "Phylactery", "buff",
            "You put something of yourself somewhere safer than here.",
            one(28, 20), cooldown=15, duration=3,
            stat_mods={"damage_taken_pct": -0.35},
            target_type="self", buff_scope="combat",
            source="CoA class tree: 'Upon taking damage which would bring "
                   "you below 10% health, become a Shade ... Reaching your "
                   "Phylactery in this state revives you with 40% of your "
                   "maximum health'. There is no cheat-death mechanic and no "
                   "world position to walk back to, so it is a heavy "
                   "mitigation window instead - the thing the Shade would "
                   "have bought. Both Death and Rime list a pre-placed "
                   "Phylactery as one of the only things that works through "
                   "a stunlock."),
    ability("ghoulify", "Ghoulify", "debuff",
            "The target spends a while being something else.",
            one(16, 20), cooldown=6, duration=2, target_type="enemy",
            is_stun=True, is_instant=True,
            source="CoA: Death's weakness list names \"Ghoulify's fear\" "
                   "among the tools that need you free to act. Fear is a "
                   "loss of control, so is_stun."),
    ability("mass_grave", "Mass Grave", "debuff",
            "Five of them go down at once and come up wrong.",
            one(34, 30), cooldown=9, duration=2, target_type="enemy_aoe",
            max_targets=5, is_stun=True,
            source="CoA class tree: 'Transform up to 5 nearby enemies into a "
                   "ghoul, fearing them for 40 seconds (8). Only affects "
                   "Humanoids.' The Humanoid restriction has no hook and is "
                   "dropped; max_targets 5 keeps the real cap."),
    ability("unholy_frenzy", "Unholy Frenzy", "buff",
            "Everything speeds up and none of it is good for anyone else.",
            one(36, 30), cooldown=10, duration=3,
            stat_mods={"haste": 20.0, "damage_dealt_pct": 15},
            target_type="self", buff_scope="combat", is_instant=True,
            source="The class's big offensive cooldown - five CoA talents "
                   "across the three trees exist only to modify it (Study of "
                   "Death, Fleshcrafting, Unstoppable Frenzy, Dominion of "
                   "Frost, Giant Bones). damage_dealt_pct is the key a BUFF "
                   "uses to raise outgoing damage (percent points, read in "
                   "Ability._damage_multiplier); the talent-side keys "
                   "spell_damage/all_damage are read through "
                   "get_talent_effect only and do nothing from a buff."),
    ability("foul_invocation", "Foul Invocation", "buff",
            "You stop pretending to be alive for a while.",
            one(44, 35), cooldown=14, duration=3,
            stat_mods={"max_health_pct": 0.3, "magic_resistance": 60},
            target_type="self", buff_scope="combat",
            source="CoA class tree: 'Transform into an undead monstrosity "
                   "for 20 seconds, increasing your maximum health by 30%. "
                   "While transformed you are immune to Fear, Sleep, Charm, "
                   "and Disease effects.' max_health_pct is a FRACTION even "
                   "from a buff - ability stat_mods and talent effects share "
                   "one bonus pool in _recalculate_derived_stats, so 0.3 is "
                   "+30% and 30.0 would be +3000%. The immunities have no "
                   "hook; the magic resistance stands in."),
    ability("call_of_the_scourge", "Call of The Scourge", "revive",
            "They are not finished. You have decided.",
            one(50, 40, 40), cooldown=20, target_type="ally",
            source="CoA: all three spec pages list 'brings combat rez', and "
                   "Animation names it: 'Call of The Scourge, an in-combat "
                   "battle res'. effect_value is the percent of max health "
                   "revived at, matching tinker_defibrillate."),

    # ---- Death: diseases
    ability("plague_of_undeath", "Plague of Undeath", "spell_dot",
            "Something old and patient takes hold, and prayers stop helping.",
            ranks(72, 22, 20, start=8, count=8), cooldown=2, duration=4,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Open by applying Plague of Undeath (Plague DoT + "
                   "reduced enemy Holy healing)'. The Holy-healing debuff is "
                   "the closest thing the spec has to support and has no "
                   "engine hook - there is no healing-received modifier a "
                   "monster reads."),
    ability("lichplague", "Lichplague", "spell_dot",
            "The last disease you apply, and the one that notices the "
            "others.",
            ranks(96, 30, 25, start=24, count=6), cooldown=3, duration=4,
            target_type="enemy", damage_school="shadow",
            source="CoA: 'Lichplague on top so it scales up per disease "
                   "already on the target' - 'Damage increased by 4% for "
                   "each Necromancer disease on the enemy'. Nothing counts "
                   "the DoTs on a target, so it is simply the largest "
                   "disease and the latest one learned."),
    ability("virulency", "Virulency", "spell_dot",
            "You reach into the rot already there and seed it everywhere "
            "else.",
            ranks(60, 18, 30, start=28, count=5), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=4, damage_school="shadow",
            source="CoA: 'Reinvigorate your diseases, refreshing all "
                   "diseases on the target enemy and copying them ... You "
                   "may use this ability again within 10 sec to Infest "
                   "another target'. Copying a live DoT package has no hook, "
                   "so the spread is expressed directly: one cast puts the "
                   "disease on up to four enemies itself."),
    ability("harvest_plague", "Harvest Plague", "damage_and_heal",
            "You drink what the disease has been making.",
            ranks(100, 30, 25, start=22, count=6), cooldown=4,
            target_type="enemy", damage_school="shadow",
            source="CoA: \"Harvest Plague's siphon, Plague Doctor and Plague "
                   "Drinker only ever feed your own health bar\" - one of "
                   "only two real sustain buttons in the Death kit."),
    ability("apothecarys_cauldron", "Apothecary's Cauldron", "buff",
            "You brew something and make everyone drink it.",
            one(46, 30), cooldown=12, duration=4,
            stat_mods={"haste": 10.0}, target_type="self",
            buff_scope="party", is_instant=True,
            source="CoA: 'Apothecary's Cauldron gives the party a spell-haste "
                   "raid buff and boosts your own Magic damage. That, plus "
                   "Plague of Undeath's Holy-healing debuff, is the closest "
                   "thing to \"support\" you bring.' A talent cannot reach an "
                   "ally (get_talent_effect reads the caster only), so the "
                   "party half is this ability and the self half is the "
                   "Death talent of the same name."),

    # ---- Rime: frost and control
    ability("ice_barrage", "Ice Barrage", "spell_dot",
            "Shard after shard, and when it stops the target is inside the "
            "ice.",
            ranks(66, 20, 25, start=18, count=7), cooldown=3, duration=2,
            target_type="enemy", damage_school="frost", is_stun=True,
            source="CoA: 'Unleash a relentless volley of glacial shards ... "
                   "At the end of the duration, you entomb your target in "
                   "ice, freezing them for 4 seconds.' The entomb is the "
                   "is_stun; the channel is a DoT."),
    ability("glacial_impact", "Glacial Impact", "spell_damage",
            "The sky drops something heavy on them.",
            ranks(80, 24, 30, start=22, count=6), cooldown=4,
            target_type="enemy", damage_school="frost",
            source="CoA: 'Use Glacial Impact on any Frozen target for its "
                   "guaranteed crit (Glacier Lord)'. The Frozen requirement "
                   "has no engine state to check - there is no Frozen flag - "
                   "so it is castable always and the Frozen-only payoffs "
                   "(Glacier Lord, Frigidness) are unconditional crit "
                   "talents instead. The spec's biggest single hit."),
    ability("command_bonefreeze", "Command: Bonefreeze", "debuff",
            "The ground goes white and nothing standing on it moves.",
            one(28, 25), cooldown=7, duration=2, target_type="enemy_aoe",
            max_targets=5, is_stun=True, is_instant=True,
            source="CoA: 'Command your Skeletal Mages to freeze enemies at "
                   "target location for 40 seconds (8 sec vs players). "
                   "Damage taken may end the effect.' The group peel Rime "
                   "opens packs with."),
    ability("heartchill", "Heartchill", "debuff",
            "Their heart skips and the words go with it.",
            one(22, 15), cooldown=5, duration=1, target_type="enemy",
            is_stun=True, is_instant=True,
            source="CoA: 'Heartchill to interrupt a caster' - 'interrupting "
                   "their current spell cast'. There is no cast bar to "
                   "interrupt in a turn engine, so a one-turn stun is the "
                   "honest equivalent: the enemy loses the action it was "
                   "about to take."),
    ability("lich_form", "Lich Form", "buff",
            "You stop being warm. It was never doing much for you.",
            one(40, 20), duration=0,
            stat_mods={"frost_spell_power": 50, "magic_resistance": 30},
            target_type="self", exclusive_group="necromancer_form",
            source="CoA: 'Lich Form is the Undead-transform become-the-Lich "
                   "cooldown ... increasing your Frost damage dealt by 10%. "
                   "While active you generate 3 Runic Power every 5 sec.' "
                   "frost_spell_power is read by "
                   "Character.get_effective_spell_power, so this really does "
                   "only scale Frost. The passive Runic Power tick has no "
                   "hook - no engine path grants a resource per turn from a "
                   "buff. Duration 0 and an exclusive_group make it a stance."),
    ability("chilling_presence", "Chilling Presence", "buff",
            "Standing near you is uncomfortable in a way that helps.",
            one(32, 25), cooldown=10, duration=4,
            stat_mods={"crit_chance_spell": 3.0, "crit_chance_physical": 3.0},
            target_type="self", buff_scope="party", is_instant=True,
            source="CoA: '\"Support\" here means Chilling Presence for the "
                   "party crit aura' - 'Increases critical strike chance of "
                   "all party and raid members by 3%'. Party-scoped for the "
                   "same reason Apothecary's Cauldron is."),
    ability("animate_frost_wyrm", "Animate: Frost Wyrm", "spell_dot",
            "Something long and dead circles overhead and keeps breathing.",
            ranks(58, 17, 35, start=40, count=4), cooldown=10, duration=3,
            target_type="enemy_aoe", max_targets=5, damage_school="frost",
            source="CoA class tree: 'Animate a Frost Wyrm that flies behind "
                   "the Necromancer that blasts nearby enemies every 2 sec "
                   "for 30 seconds'. NOT a summon_pet: effect_type 'summon' "
                   "does nothing, the engine only handles 'summon_pet' with "
                   "a summon_pet_template that already exists in "
                   "combat/pet_templates.py, and there is no frost-wyrm "
                   "template (nor may one be added). A pet whose only job is "
                   "to tick AoE damage on a timer IS a persistent AoE DoT, "
                   "so that is what it is - the honest version, rather than "
                   "the four Tinker abilities that shipped as 'summon' and "
                   "summoned nothing for months."),

    # ---- Animation: the army
    ability("raise_ghoul", "Raise: Ghoul", "summon_pet",
            "It gets up faster than you expect every time.",
            one(8, 20, 100), target_type="self", is_instant=True,
            summon_pet_template="ghoul", additional_pet=True,
            source="CoA: 'Raise a Ghoul to aid you in combat occupying 1 "
                   "Life Force. Its auto attacks restore SP health to you. "
                   "Command: Expels leeching plague that strikes up to 5 "
                   "nearby enemies, dealing Intellect Plague damage, and "
                   "healing you for Intellect for each Ghoul.' NOW A REAL "
                   "GHOUL. This was 'wolf' and summoned a pet named Wolf - "
                   "the old note here recorded that as a deliberate mapping "
                   "because 'no undead pet template exists and none may be "
                   "added'. Both halves of that have since changed: multi-pet "
                   "support landed (Character.EXTRA_PET_CAP gives Necromancer "
                   "3 pets beyond active_pet, hence additional_pet below), "
                   "which stood Wolf, Imp, Succubus and Faceless Destroyer on "
                   "the field together, and combat/pet_templates.py now "
                   "carries a real 'ghoul' - melee, level_req 8 to match this "
                   "ability, with its CoA leech implemented as a "
                   "damage_and_heal that genuinely smart-heals the owner's "
                   "lowest-health party member. The 5-target Command plague "
                   "is still not expressible (pet AoE is dead in both "
                   "directions - see that file's SUMMON_THEME_SOURCE), and "
                   "the Animation tree's Vampiric Aura talent still carries "
                   "its own on-hit leech separately."),
    ability("raise_skeletal_mage", "Raise: Skeletal Mage", "summon_pet",
            "A thin one, still holding its staff.",
            one(14, 25, 100), target_type="self", is_instant=True,
            summon_pet_template="skeletal_mage", additional_pet=True,
            source="CoA Rime: 'Raise a Skeletal Mage to aid you in combat, "
                   "occupying 2 Life Force. Command: Unleashes ice at your "
                   "target and enemies within 6 yds, dealing frost SP Frost "
                   "damage'. NOW A REAL SKELETAL MAGE. This was 'imp' and "
                   "summoned a pet named Imp with Firebolt - the right SHAPE "
                   "(base_attack 0, real base_spell_power, one nuke) and the "
                   "wrong name, wrong school and wrong class's numbers. "
                   "combat/pet_templates.py now carries 'skeletal_mage', a "
                   "Frost caster at level_req 14 to match this ability. "
                   "Rime's rotation opens with 'Raise a Skeletal Mage "
                   "first', which is why it is the earliest caster pet. The "
                   "Command's 6-yard splash is not expressible."),
    ability("raise_banshee", "Raise: Banshee", "summon_pet",
            "She was loud in life too.",
            one(20, 25, 100), target_type="self", is_instant=True,
            summon_pet_template="banshee", additional_pet=True,
            source="CoA class tree: 'Raise a Banshee to aid you in combat, "
                   "occupying 2 Life Force. It will channel on your target, "
                   "dealing damage and draining their mana over time. "
                   "Command: Drains 20% of your target's mana ... and deals "
                   "Frost damage equal to the mana drained'. NOW A REAL "
                   "BANSHEE. This was 'succubus' and summoned a pet named "
                   "Succubus casting Lash of Pain and Seduction - a Warlock "
                   "demon on a Necromancer. combat/pet_templates.py now "
                   "carries 'banshee' at level_req 20 to match this ability: "
                   "Shadow wail plus a Frost Mana Siphon "
                   "(damage_and_restore_mana). The TARGET-SIDE drain still "
                   "has no hook - nothing in this engine reduces an enemy's "
                   "resource pool - so the siphon refills the Banshee, not "
                   "the Necromancer; that limit is written out in the "
                   "template's own _source."),
    ability("raise_abomination", "Raise: Abomination", "summon_pet",
            "Several people, eventually.",
            one(30, 30, 100), target_type="self", is_instant=True,
            summon_pet_template="abomination", additional_pet=True,
            source="CoA class tree: 'Raise an Abomination to aid you in "
                   "combat, occupying 3 Life Force. It is surrounded by a "
                   "disease cloud, dealing SP Nature damage to enemies when "
                   "they deal damage and reducing their attack speed by 20% "
                   "for 15 seconds'. NOW A REAL ABOMINATION. This was "
                   "'faceless_destroyer' and summoned the Cultist's pet - "
                   "picked at the time for being the toughest melee template "
                   "in the roster, which is the right instinct for a "
                   "3-Life-Force raise and the wrong creature. "
                   "combat/pet_templates.py now carries 'abomination' at "
                   "level_req 30 to match this ability: the slowest, most "
                   "armoured of the four raises, with a real Nature Disease "
                   "Cloud. The cloud's AREA and the -20% attack speed are "
                   "still not expressible on a pet (a pet never casts a "
                   "debuff, and pet AoE is dead); Animation's Flesh "
                   "Symbiosis talent still carries the per-Abomination "
                   "armour."),
    ability("animate_skeletal_archers", "Animate: Skeletal Archers",
            "spell_damage",
            "Three of them, and none of them need to breathe before they "
            "loose.",
            ranks(40, 12, 25, start=12, count=8), cooldown=3,
            target_type="enemy_aoe", max_targets=4, damage_school="shadow",
            source="CoA: 'Dump generated RP into Animate: Skeletal Archers "
                   "for instant ranged bodies' - 'Animate 3 Skeletal Archers "
                   "to aid you in combat for 15 seconds'. Three bodies at "
                   "once cannot be pets: active_pet holds exactly one, and "
                   "there is no archer template. A 15-second volley of "
                   "ranged undead is AoE damage, so that is what it is."),
    ability("animate_plaguefather", "Animate: Plaguefather", "spell_dot",
            "He walks into the middle of them and starts leaking.",
            ranks(44, 13, 30, start=24, count=6), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=4, damage_school="shadow",
            source="CoA: 'Plaguefather smears Zombie Plague' - 'Damage dealt "
                   "by this minion will emit Zombie Plague, dealing SP "
                   "Plague damage to nearby enemies, and reducing their "
                   "attack power'. Same template problem as the Archers; a "
                   "walking AoE plague source is an AoE DoT."),
    ability("animate_bone_wraith", "Animate: Bone Wraith", "dot",
            "It comes apart on purpose and the pieces keep swinging.",
            ranks(36, 11, 30, start=30, count=5), cooldown=6, duration=3,
            target_type="enemy_aoe", max_targets=5,
            source="CoA: 'it will periodically unleash a Bonestorm, striking "
                   "up to 5 nearby enemies for SP Physical damage every 1 "
                   "sec for 5 seconds'. effect_type 'dot' with no "
                   "damage_school, so it lands as physical - the one "
                   "physical-damage ability in the whole kit, which is "
                   "exactly what CoA says Bonestorm is."),
    ability("animate_tomb_king", "Animate: Tomb King", "buff",
            "He does not fight. He expects.",
            one(34, 30), cooldown=12, duration=4,
            stat_mods={"damage_dealt_pct": 12, "attack_power": 40},
            target_type="self", buff_scope="combat", is_instant=True,
            source="CoA: 'Keep Tomb King up so every minion attack hits "
                   "harder' - 'all of your Undead minion's attacks deal an "
                   "additional 10% of the damage dealt as Plague damage'. A "
                   "Pet reads only three talent keys off its owner "
                   "(pet_damage/pet_health/pet_armor, see entities/pet.py) "
                   "and nothing at all off the owner's buffs, so a buff "
                   "cannot reach a minion. This raises the Necromancer's own "
                   "damage instead and the tree's pet_damage nodes carry the "
                   "minion half."),
    ability("march_of_the_dead", "March of the Dead", "spell_damage",
            "They set off towards the enemy and do not arrive intact.",
            ranks(70, 20, 35, start=36, count=4), cooldown=6,
            target_type="enemy_aoe", max_targets=5, damage_school="shadow",
            source="CoA: 'March of the Dead is your AoE plague nuke' - 'When "
                   "they reach an enemy they explode, dealing SP Plague "
                   "damage to nearby enemies and slowing their movement "
                   "speed by 70%'. The slow has no hook."),
    ability("sacrifice_undead", "Sacrifice Undead", "heal",
            "You thank it, and then you use it.",
            ranks(200, 60, 15, start=20, count=6), cooldown=6,
            target_type="self", is_instant=True,
            source="CoA: 'Sacrifice Undead converts a destroyed pet into a "
                   "max-HP heal' - one of the three things that keep "
                   "Animation alive. The pet is not actually consumed: there "
                   "is no ability-level hook to destroy active_pet, so this "
                   "is a plain self-heal and the cost is Life Force rather "
                   "than a minion."),
    ability("corpse_wagon", "Corpse Wagon", "buff",
            "It creaks past and everyone fights a little harder for reasons "
            "they would rather not examine.",
            one(42, 30), cooldown=12, duration=4,
            stat_mods={"damage_dealt_pct": 5}, target_type="self",
            buff_scope="party", is_instant=True,
            source="CoA: 'Corpse Wagon adds a party/raid damage aura for the "
                   "group' - 'Increases all damage dealt by party and raid "
                   "members by 3%'. damage_dealt_pct is percent points from "
                   "a buff. Party-scoped; the Animation talent of the same "
                   "name carries only the self half."),
]


# ============================================================ talent helpers

def node(tree, tid, name, description, tier, slot, max_points, effects,
         *, node_type="passive", connect=None, proc=None, source=None,
         total_slots=4):
    """One talent node. `slot` is 0-based across the tier's row.

    Hex layout copies the shipped trees: hex_y = -6 + 2*tier, hex_x spaced
    by 2 and centred on the row, so the tiers narrow toward the capstone.
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


def life_force_proc(chance, amount, *, icd=1, filter_ids=None,
                    trigger="on_damage_cast"):
    """A proc that hands back Life Force.

    grant_resource routes through Character.gain_resource, the same method
    every builder/spender ability uses, so it respects the 100 cap. Only the
    `chance` scales with rank (_sync_talent_procs multiplies it by
    points_spent); the amount does not, which is why every multi-rank proc
    node below words its tooltip as "N% chance per rank".
    """
    proc = {"trigger": trigger, "chance": chance, "icd": icd,
            "grant_resource": {"resource": "life_force", "amount": amount}}
    if filter_ids:
        proc["ability_filter"] = [f"necromancer_{i}" for i in filter_ids]
    return proc


def disease_proc(chance, potency, effect_id, name, *, icd=0, filter_ids=None,
                 trigger="on_damage_cast", stacks=None, duration=3):
    """A proc that plants a Shadow DoT on the target."""
    effect = {
        "effect_id": f"necromancer_{effect_id}",
        "name": name,
        "effect_type": "dot",
        "duration": duration,
        "potency": potency,
        "damage_school": "shadow",
        "on_target": True,
    }
    if stacks:
        effect["max_stacks"] = stacks
    proc = {"trigger": trigger, "chance": chance, "icd": icd,
            "apply_effect": effect}
    if filter_ids:
        proc["ability_filter"] = [f"necromancer_{i}" for i in filter_ids]
    return proc


# ================================================================== Death
D = "necromancer_death"
DEATH = tree(
    D, "Necromancer Death",
    "Disease throughput - layer plagues on a target, let them stack, then "
    "make every tick count for more.",
    [
        node(D, "damnation", "Damnation",
             "Increases your Shadow damage by 2% per rank.",
             0, 0, 5, {"shadow_spell_damage": 0.02},
             source="CoA: 'Increases your Shadow damage by 5%, doubled "
                    "against enemies below 35% health.' The below-35% "
                    "doubling has no hook - _damage_multiplier never sees "
                    "the recipient's health on a damage cast - so this is "
                    "the flat half only. Every disease in this kit is "
                    "Shadow, so it scales the whole spec."),
        node(D, "cycle_of_death", "Cycle of Death",
             "Increases your haste by 1 per rank.",
             0, 1, 5, {"haste": 1.0},
             source="CoA: 'Increases your spell haste by 5%.' Haste is "
                    "second in this spec's own stat priority, behind Spell "
                    "Hit."),
        node(D, "dark_harvester", "Dark Harvester",
             "Increases your spell critical strike chance by 1% and your hit "
             "rating by 1 per rank.",
             0, 2, 5, {"crit_chance_spell": 1.0, "hit_rating": 1},
             source="CoA: 'Increases your critical strike and hit chance by "
                    "3%.' Spell Hit leads the stat priority ('until your "
                    "spells stop missing a +3-level target'), so the hit "
                    "half is the point of the node."),
        node(D, "rotting_flesh", "Rotting Flesh",
             "Increases the damage of Flesh to Worms by 6% per rank.",
             0, 3, 5, {"ability_necromancer_flesh_to_worms_damage": 0.06},
             source="CoA: 'Increases the damage of Flesh to Worms by 25% and "
                    "allows its periodic damage to scale with your spell "
                    "haste.' DoT ticks do not read haste here, so the damage "
                    "half carries the node."),

        node(D, "swarmer", "Swarmer",
             "Crypt Swarm has a 33% chance per rank to restore 4 Life Force.",
             1, 0, 3, {}, connect=["damnation"],
             proc=life_force_proc(33, 4, icd=0, filter_ids=["crypt_swarm"]),
             source="CoA: 'Increases the Runic Power generated by Crypt Swarm "
                    "by 2 per tick.' An ability's `generates` amount is not "
                    "talentable, so the extra fuel arrives as a proc on the "
                    "same cast instead. Mechanically identical from the "
                    "player's side: Crypt Swarm pays more."),
        node(D, "necrosis", "Necrosis",
             "Increases the duration of your diseases by 6% per rank.",
             1, 1, 3, {"dot_duration_pct": 0.06}, connect=["cycle_of_death"],
             source="CoA: 'Increases the duration of your diseases by 25%.' "
                    "dot_duration_pct is the real key, read on the DoT path."),
        node(D, "unholy_runes", "Unholy Runes",
             "Increases the damage of Crypt Swarm by 6% per rank.",
             1, 2, 5, {"ability_necromancer_crypt_swarm_damage": 0.06},
             connect=["dark_harvester"],
             source="CoA: 'Increases the damage of Crypt Swarm by 15%.' "
                    "Crypt Swarm is the cast this spec presses most, so this "
                    "is the deepest single-ability node in the tree."),
        node(D, "festering_decay", "Festering Decay",
             "Reduces the Life Force cost of your abilities by 2% per rank.",
             1, 3, 5, {"all_ability_cost_pct": 0.02},
             connect=["rotting_flesh"],
             source="CoA: 'Reduces the cost of Command spells by -15% and "
                    "causes them to increase the target's spell damage taken "
                    "by 10% for 15 seconds.' The enemy half is dead against "
                    "monsters - Monster reads only armor and attack_power off "
                    "its status effects - so the node is the cost reduction, "
                    "widened from Command spells to everything because "
                    "nothing groups abilities by CoA school."),

        node(D, "crypt_plague", "Crypt Plague",
             "Crypt Swarm and Lichfrost have a 33% chance per rank to apply "
             "Crypt Plague, a Shadow disease that stacks up to 5 times.",
             2, 0, 3, {}, connect=["swarmer"],
             proc=disease_proc(33, 42, "crypt_plague", "Crypt Plague",
                               filter_ids=["crypt_swarm", "lichfrost"],
                               stacks=5),
             source="CoA's own level-10 passive: 'Damage dealt by Crypt Swarm "
                    "now applies 1 stack of Crypt Plague and Lichfrost "
                    "applies 2 stacks. Deals SP Plague Damage every 2 sec for "
                    "10 seconds, stacking 10 times.' Frontier has no free "
                    "level passives, so it costs points. Two stacks from "
                    "Lichfrost is not expressible (one proc, one stack), and "
                    "the cap is 5 rather than 10 - no shipped stacking debuff "
                    "goes past 5."),
        node(D, "plague_science", "Plague Science",
             "Increases the damage your periodic effects deal by 4% per rank.",
             2, 1, 3, {"dot_damage": 0.04}, connect=["necrosis"],
             source="CoA's level-20 passive: 'Your diseases and Crypt Swarm "
                    "now deal 100% increased damage to enemies below 20% "
                    "health.' The execute condition has no hook on the DoT "
                    "path, so it is an unconditional, far smaller DoT bonus."),
        node(D, "fiend", "Fiend",
             "Increases the damage of Lichfrost by 6% per rank.",
             2, 2, 3, {"ability_necromancer_lichfrost_damage": 0.06},
             connect=["unholy_runes"],
             source="CoA: 'Increases the damage and critical damage of "
                    "Lichfrost by 20% against diseased targets.' Nothing "
                    "counts diseases on a target, so it applies always and at "
                    "a fraction of the value."),
        node(D, "mutation", "Mutation",
             "Increases the damage of your Shadow periodic effects by 2% per "
             "rank.",
             2, 3, 5, {"shadow_dot_damage": 0.02},
             connect=["festering_decay"],
             source="CoA: 'For the next 15 seconds your diseases mutate "
                    "causing them to act with accelerated lethality, allowing "
                    "your freshly applied diseases to tick -50% faster.' Tick "
                    "RATE is not a thing in a turn engine; faster ticks are "
                    "more damage, so that is what the node grants. "
                    "shadow_dot_damage is assembled at runtime as "
                    "f'{school}_dot_damage' - a literal grep calls it dead."),

        node(D, "expunge", "Expunge",
             "Applying a disease increases your damage dealt by 5% for 3 "
             "turns.",
             3, 0, 1, {}, connect=["crypt_plague"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "ability_filter": ["necromancer_flesh_to_worms",
                                      "necromancer_plague_of_undeath",
                                      "necromancer_lichplague"],
                   "apply_effect": {
                       "effect_id": "necromancer_expunge",
                       "name": "Expunge",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"damage_dealt_pct": 5},
                       "on_target": False}},
             source="CoA: 'Increases the target's damage taken from your "
                    "Necromancer diseases by 10% for 10 seconds, stacking 2 "
                    "times.' That is an enemy debuff, and a monster reads "
                    "neither magic_damage_taken_pct nor "
                    "spell_damage_taken_pct off its status effects, so the "
                    "bonus is moved onto the caster where it works. One rank "
                    "only: a proc's payload does not scale with points, just "
                    "its chance, and this one is already at 100%."),
        node(D, "plague_revenant", "Plague Revenant",
             "Your critical strikes have a 25% chance per rank to apply Crypt "
             "Plague.",
             3, 1, 3, {}, connect=["plague_science"],
             proc=disease_proc(25, 38, "plague_revenant", "Crypt Plague",
                               trigger="on_crit", icd=1, stacks=5),
             source="CoA: 'Critical strikes now apply a stack of Crypt "
                    "Plague.' Guaranteed in CoA; a chance here, because a "
                    "multi-rank node needs something to scale and the chance "
                    "is the only thing that does."),
        node(D, "apothecarys_cauldron", "Apothecary's Cauldron",
             "Increases your spell damage by 2% per rank.",
             3, 2, 5, {"spell_damage": 0.02}, connect=["fiend"],
             source="CoA: 'Increases the spell haste of all party and raid "
                    "members by 3% ... In addition, increases your Magic "
                    "damage dealt by 3%.' Only the self half can be a talent; "
                    "the party haste is the ability of the same name."),
        node(D, "foul_contagion", "Foul Contagion",
             "Flesh to Worms lasts 1 turn longer per rank.",
             3, 3, 2, {"ability_necromancer_flesh_to_worms_duration": 1},
             connect=["mutation"],
             source="CoA: 'Applying Crypt Plague now extends the duration of "
                    "Flesh to Worms on the target by 1 sec.' The trigger is "
                    "not expressible, the effect is: ability_<id>_duration "
                    "keys are built by interpolation in abilities.py."),

        node(D, "pandemic", "Pandemic",
             "Reduces the cooldown of Virulency by 8% per rank.",
             4, 0, 3, {"ability_necromancer_virulency_cooldown_pct": 0.08},
             connect=["expunge"],
             source="CoA: 'Damage dealt by your Undead minions now reduces "
                    "the cooldown of Virulency by -1 sec.' A positive "
                    "_cooldown_pct is a reduction (talented_cooldown), with a "
                    "hard floor of 1 turn."),
        node(D, "rot_fetishist", "Rot Fetishist",
             "Virulency hits for an additional 20% of its damage.",
             4, 1, 1, {}, connect=["plague_revenant"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 1,
                   "ability_filter": ["necromancer_virulency"],
                   "bonus_pct": 0.2},
             source="CoA: 'Your Virulency now applies Rot Fetishist for 10 "
                    "seconds, causing you to replicate 20% of your periodic "
                    "damage dealt as direct damage.' Nothing can read a "
                    "running DoT's tick and mirror it, so the replication "
                    "lands on the cast that would have applied it - bonus_pct "
                    "adds extra damage to the same hit."),
        node(D, "creeping_plagues", "Creeping Plagues",
             "Increases the damage your area effects deal by 8% per rank.",
             4, 2, 3, {"aoe_damage": 0.08}, connect=["apothecarys_cauldron"],
             source="CoA: 'You may now Infest an additional target after "
                    "using Virulency.' One more target is more area damage, "
                    "and aoe_damage is the key the engine reads for every "
                    "enemy_aoe cast - which is Virulency, Crypt Explosion's "
                    "Corpse Explosion and the whole Animate line."),

        node(D, "touch_of_death", "Touch of Death",
             "Increases your Shadow spell power by 10 per rank.",
             5, 0, 3, {"shadow_spell_power": 10}, connect=["pandemic"],
             total_slots=3,
             source="CoA: 'Allows Expunge to stack an additional time and "
                    "increases the range of your Death spells by 20%.' "
                    "Neither stacking caps nor spell range exist here, so the "
                    "node buys raw Shadow power instead - read by "
                    "get_effective_spell_power, so it really does only scale "
                    "the diseases."),
        node(D, "death_commander", "Death Commander",
             "Your damage spells have a 20% chance per rank to increase your "
             "haste by 20 for 3 turns.",
             5, 1, 2, {}, connect=["rot_fetishist"], total_slots=3,
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 2,
                   "apply_effect": {
                       "effect_id": "necromancer_death_commander",
                       "name": "Death Commander",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"haste": 20.0},
                       "on_target": False}},
             source="CoA: 'Periodic damage dealt now has a 10% chance to "
                    "increase your and your Undead minion's haste by 20% for "
                    "8 seconds.' A DoT tick is not a proc trigger here, so it "
                    "fires off the cast. The minion half cannot be reached by "
                    "a buff."),
        node(D, "unholy_erosion", "Unholy Erosion",
             "Increases your spell penetration by 20 per rank.",
             5, 2, 2, {"spell_penetration": 20},
             connect=["creeping_plagues"], total_slots=3,
             source="CoA's level-50 passive: 'Increases your spell "
                    "penetration by 50, scaling with your level.' A real "
                    "stat - take_damage subtracts the attacker's "
                    "spell_penetration from the defender's resistance, on "
                    "both Character and Monster."),

        node(D, "waking_crypts", "Waking Crypts",
             "Every disease you have running bites deeper, and the swarm "
             "itself hits harder.",
             6, 0, 1, {"dot_damage": 0.15, "shadow_spell_damage": 0.06},
             connect=["touch_of_death", "death_commander", "unholy_erosion"],
             total_slots=1,
             source="Capstone. CoA: 'Increases the damage of Crypt Plague by "
                    "50% and Crypt Swarm now deals 4% more damage for each "
                    "Necromancer disease you have on the target.' The "
                    "per-disease count has no hook, so the payoff is flat: "
                    "the whole DoT pool and the whole Shadow school. Matches "
                    "what CoA rates the spec on - 'It snowballs the longer "
                    "your DoTs stay up.'"),
    ],
    "Built from reference/coa_sidekick/SPEC_necromancer__death.txt and the "
    "39 'death' nodes in reference/coa_sidekick/talents/necromancer.json. CoA "
    "calls this the Unholy/Blood Death Knight analog 'with an Affliction "
    "Warlock veneer' and its one-line summary is 'Pure disease throughput'. "
    "The tree spends accordingly: almost every node either applies a "
    "disease, extends one, or multiplies what one tick does. Its stat "
    "priority is Spell Hit > Haste > Spell Power > Crit > Intellect > "
    "Spirit/MP5, which is why Dark Harvester carries hit rating and Cycle of "
    "Death is a 5-point haste node at tier 0. CoA's own weakness list is the "
    "honest shape of it: 'Damage is stack-based ... so the first seconds of a "
    "burst opener find you weak', and 'There is no interrupt'.")


# =================================================================== Rime
R = "necromancer_rime"
RIME = tree(
    R, "Necromancer Rime",
    "Frost and hard control - freeze a target, then drop something heavy on "
    "it, with a raised caster working the whole time.",
    [
        node(R, "runic_reservoir", "Runic Reservoir",
             "Increases your Frost damage by 2% per rank.",
             0, 0, 5, {"frost_spell_damage": 0.02},
             source="CoA: 'Increases your Frost damage by 5% and your maximum "
                    "Runic Power by 15.' The pool half wanted life_force_max, "
                    "which Character.get_resource_max genuinely reads but "
                    "tools/audit_talents.py's hardcoded _NAMED_LIVE set does "
                    "not list, so the validator calls it dead and it is left "
                    "out rather than shipped as a key the tooling will keep "
                    "flagging. Frost damage only."),
        node(R, "bone_legion", "Bone Legion",
             "Increases the damage of Lichfrost by 6% per rank.",
             0, 1, 5, {"ability_necromancer_lichfrost_damage": 0.06},
             source="CoA: 'Increases the damage of Lichfrost by 10% and its "
                    "Runic Power generated by 25%.' The generation half is "
                    "not talentable; Freeze Dry below is where extra Life "
                    "Force comes from."),
        node(R, "hoarfrost_hands", "Hoarfrost Hands",
             "Increases your hit rating by 1 per rank.",
             0, 2, 5, {"hit_rating": 1},
             source="CoA: 'Increases the duration of Lichfrost's movement "
                    "speed slow by 4 sec and your hit chance by 4%.' Slows do "
                    "not exist on a monster, hit does, and Spell Hit is first "
                    "in this spec's stat priority."),
        node(R, "curse_of_the_lich", "Curse of the Lich",
             "Increases your spell critical strike chance by 1% per rank.",
             0, 3, 5, {"crit_chance_spell": 1.0},
             source="CoA: 'Increases the range of your Rime spells by 6 yds "
                    "and increases the Frost critical strike chance of you "
                    "and your summons by 3%.' Range has no hook and crit is "
                    "not per-school; the summon half is Death and Ice."),

        node(R, "piercing_icicles", "Piercing Icicles",
             "Increases the damage of Ice Barrage by 8% per rank.",
             1, 0, 3, {"ability_necromancer_ice_barrage_damage": 0.08},
             connect=["runic_reservoir"],
             source="CoA: 'Increases the damage of Ice Barrage by 20%.'"),
        node(R, "frigid_death", "Frigid Death",
             "Increases the damage of Glacial Impact by 8% per rank.",
             1, 1, 3, {"ability_necromancer_glacial_impact_damage": 0.08},
             connect=["bone_legion"],
             source="CoA: 'Increases the damage of Glacial Impact by 20%.' "
                    "Glacial Impact is the spike the whole spec sets up."),
        node(R, "freeze_dry", "Freeze Dry",
             "Glacial Impact has a 20% chance per rank to restore 6 Life "
             "Force.",
             1, 2, 5, {}, connect=["hoarfrost_hands"],
             proc=life_force_proc(20, 6, filter_ids=["glacial_impact"]),
             source="CoA: 'Your Glacial Impact now generates 20 Runic Power.' "
                    "The payoff cast paying for itself, which is the whole "
                    "point of CoA's dual-resource Rime loop - here it is one "
                    "pool, so the refund is smaller and chance-based."),
        node(R, "frigid_power", "Frigid Power",
             "Increases your Frost spell power by 10 per rank.",
             1, 3, 5, {"frost_spell_power": 10},
             connect=["curse_of_the_lich"],
             source="CoA: 'Increases the spell power scaling of Lichfrost and "
                    "Ice Barrage by 20%.' Per-ability spell power scaling is "
                    "not a key; Frost spell power is, and both of those "
                    "abilities are Frost."),

        node(R, "glacier_lord", "Glacier Lord",
             "Increases your spell critical strike chance by 2% per rank.",
             2, 0, 3, {"crit_chance_spell": 2.0}, connect=["piercing_icicles"],
             source="CoA: 'Your Glacial Impact is now guaranteed to "
                    "critically strike against Frozen targets.' There is no "
                    "Frozen state in the engine and no per-ability crit "
                    "guarantee, so the node buys real crit chance instead - "
                    "the same mechanic, paid for honestly."),
        node(R, "frigidness", "Frigidness",
             "Increases the critical strike damage of your Frost spells by "
             "10% per rank.",
             2, 1, 3, {"frost_crit_damage_pct": 0.10}, connect=["frigid_death"],
             source="CoA: 'Increases your critical damage by 50% against "
                    "Frozen targets.' <school>_crit_damage_pct is a real "
                    "runtime-built key, read in _crit_damage_bonus against "
                    "the school the cast actually deals. Unconditional, since "
                    "Frozen does not exist."),
        node(R, "arch_lich", "Arch Lich",
             "Your critical strikes have a 33% chance per rank to restore 5 "
             "Life Force.",
             2, 2, 3, {}, connect=["freeze_dry"],
             proc=life_force_proc(33, 5, trigger="on_crit"),
             source="CoA: 'Critical strikes with Frost spells now refund 3% "
                    "of your maximum mana.' A Necromancer has no Mana pool at "
                    "all (_recalculate_derived_stats only builds one for "
                    "Mana-resource classes), so the refund is Life Force."),
        node(R, "deathly_chill", "Deathly Chill",
             "Reduces the cooldown of Ice Barrage by 6% per rank.",
             2, 3, 5, {"ability_necromancer_ice_barrage_cooldown_pct": 0.06},
             connect=["frigid_power"],
             source="CoA: 'Reduces the channel and cast time of Ice Barrage "
                    "by -25%.' Cast time is not modelled; a cooldown is the "
                    "closest thing to 'you get to do this more often'."),

        node(R, "necrotic_chains", "Necrotic Chains",
             "Glacial Impact and Command: Bonefreeze freeze their target in "
             "place, no more than once every 3 turns.",
             3, 0, 1, {}, connect=["glacier_lord"],
             proc={"trigger": "on_damage_cast", "chance": 100, "icd": 3,
                   "ability_filter": ["necromancer_glacial_impact",
                                      "necromancer_command_bonefreeze"],
                   "apply_effect": {
                       "effect_id": "necromancer_necrotic_chains",
                       "name": "Necrotic Chains",
                       "effect_type": "debuff",
                       "duration": 1,
                       "stat_mods": {},
                       "is_stun": True,
                       "on_target": True}},
             source="CoA: 'Every 3rd Command spell now freezes the target in "
                    "place for 5 seconds.' Nothing counts casts, but a proc's "
                    "internal cooldown does the same job: icd 3 means at most "
                    "one freeze every three turns. One rank, because a 100% "
                    "chance has nothing left to scale."),
        node(R, "permafrost", "Permafrost",
             "Increases your Frost damage by 2% per rank.",
             3, 1, 3, {"frost_spell_damage": 0.02}, connect=["frigidness"],
             source="CoA: 'Gives your spells a 15% chance to grant you the "
                    "Permafrost, which treats your next 2 spells cast as the "
                    "target were Frozen.' Frozen is not a state the engine "
                    "has, so there is nothing to pretend about - the node is "
                    "the Frost damage the pretence was worth."),
        node(R, "icecrown", "Icecrown",
             "Increases your spell critical strike chance by 1% per rank.",
             3, 2, 3, {"crit_chance_spell": 1.0}, connect=["arch_lich"],
             source="CoA: 'Your Frost damage dealt now increases your allies' "
                    "critical strike chance against the enemy by 1% for 10 "
                    "seconds, stacking 3 times.' A talent is read off its own "
                    "character only, so the ally half is impossible here - "
                    "the Chilling Presence ability carries the party crit "
                    "aura instead and this is the self share."),
        node(R, "death_and_ice", "Death and Ice",
             "Increases your minion's damage by 4% per rank.",
             3, 3, 4, {"pet_damage": 0.04}, connect=["deathly_chill"],
             source="CoA: 'While a Skeletal Mage is active the critical "
                    "strike chance of your Undead minions is now increased by "
                    "10%.' pet_damage is one of exactly three owner talent "
                    "keys a Pet reads (see entities/pet.py) and it is a "
                    "FRACTION - 0.04 is +4%. Pet crit is not one of them."),

        node(R, "frozen_bodies", "Frozen Bodies",
             "Your critical strikes have a 25% chance per rank to increase "
             "your damage dealt by 6% for 3 turns.",
             4, 0, 3, {}, connect=["necrotic_chains"],
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "apply_effect": {
                       "effect_id": "necromancer_frozen_bodies",
                       "name": "Frozen Bodies",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"damage_dealt_pct": 6},
                       "on_target": False}},
             source="CoA: 'When you kill an enemy ... or critically strike "
                    "with Frost damage you now gain a stack of Frozen Bodies. "
                    "Increases the damage of your next Glacial Impact by 3%, "
                    "stacking 10 times.' Banked stacks that only one ability "
                    "can spend have no hook, so it is a short damage window "
                    "off the same trigger."),
        node(R, "champion_of_kelthuzad", "Champion of Kel'Thuzad",
             "Raise: Skeletal Mage costs 10 less Life Force.",
             4, 1, 1, {"ability_necromancer_raise_skeletal_mage_cost": 10},
             connect=["permafrost"],
             source="CoA: 'Your Skeletal Mages now only cost 1 Life Force.' "
                    "In CoA Life Force is a minion budget; here it is the "
                    "class's spending pool, so 'costs less of it' is the same "
                    "sentence. ability_<id>_cost is a flat reduction, applied "
                    "before any percentage one."),
        node(R, "blood_and_ice", "Blood and Ice",
             "Increases your minion's health by 5% per rank.",
             4, 2, 3, {"pet_health": 0.05}, connect=["icecrown"],
             source="CoA: 'Each Skeletal Warrior or Skeletal Rogue now "
                    "increases the damage of your Ice Barrage by 8%.' Nothing "
                    "counts active minions, and only one pet can be active at "
                    "a time, so the node keeps the one half that works: the "
                    "minion lasts longer. pet_health is a FRACTION."),

        node(R, "harrowing_winds", "Harrowing Winds",
             "Increases the damage your area effects deal by 8% per rank.",
             5, 0, 3, {"aoe_damage": 0.08}, connect=["frozen_bodies"],
             total_slots=3,
             source="CoA: 'Damage dealt by Glacial Impact now deals an "
                    "additional 50% of the damage dealt as Frost damage to "
                    "enemies within 6 yds of the primary target.' Glacial "
                    "Impact is single-target here, so the splash lands on the "
                    "spec's real AoE - Animate: Frost Wyrm and Command: "
                    "Bonefreeze's follow-ups."),
        node(R, "master_lich", "Master Lich",
             "Increases your Frost damage by 3% per rank.",
             5, 1, 2, {"frost_spell_damage": 0.03},
             connect=["champion_of_kelthuzad"], total_slots=3,
             source="CoA: 'Soulfreeze now increases the enemy's Frost damage "
                    "taken by you by 5% per tick for 8 sec, stacking 3 "
                    "times.' An enemy's frost_damage_taken_pct is read off "
                    "status effects on a Character but not on a Monster, so "
                    "the increase sits on the caster's own Frost damage."),
        node(R, "raising_the_kirin_tor", "Raising the Kirin Tor",
             "Your damage spells have a 20% chance per rank to restore 8 Life "
             "Force.",
             5, 2, 2, {}, connect=["blood_and_ice"], total_slots=3,
             proc=life_force_proc(20, 8),
             source="CoA: 'Your Command spells now have a 40% chance to refund "
                    "a portion of their Runic Power cost.' Nothing groups "
                    "abilities into CoA's Command school, so it fires off any "
                    "damage cast at half the chance."),

        node(R, "army_of_the_north", "Army of the North",
             "What you have raised fights like it remembers being alive, and "
             "the cold comes off you harder.",
             6, 0, 1, {"pet_damage": 0.15, "frost_spell_damage": 0.08},
             connect=["harrowing_winds", "master_lich",
                      "raising_the_kirin_tor"],
             total_slots=1,
             source="Capstone. CoA: 'Chant a powerful ritual that brings "
                    "forth 1 Rotting Frost Giant near you ... For the "
                    "duration, your Undead minions are guaranteed to "
                    "critically strike.' There is no frost-giant pet template "
                    "and none may be added, and a talent cannot summon, so "
                    "the capstone is what the Giant and the guaranteed crits "
                    "were worth: a permanently stronger minion and more "
                    "Frost damage."),
    ],
    "Built from reference/coa_sidekick/SPEC_necromancer__rime.txt and the 41 "
    "'rime' nodes in reference/coa_sidekick/talents/necromancer.json. CoA: "
    "'Closest to a Frost Death Knight reskinned as a pure ranged caster with "
    "an Unholy DK pet layer bolted on ... The payoff loop is "
    "freeze-then-detonate.' The freeze half is the honest casualty of this "
    "port - the engine has no Frozen state, so Glacier Lord, Frigidness, "
    "Permafrost and Master Lich all become unconditional crit and Frost "
    "damage rather than conditional ones. What survives intact is the rest of "
    "the identity: a frost caster that keeps a raised minion up (Death and "
    "Ice, Blood and Ice, Champion of Kel'Thuzad) and funds its own payoff "
    "casts (Freeze Dry, Arch Lich, Raising the Kirin Tor). Stat priority is "
    "Spell Hit > Spell Power > Crit > Haste > Intellect > Spirit/MP5, which "
    "is why this tree carries two flat Frost spell power nodes where Death "
    "carries haste.")


# ============================================================== Animation
A = "necromancer_animation"
ANIMATION = tree(
    A, "Necromancer Animation",
    "An army instead of a rotation - keep minions standing, flood the field "
    "with short-lived undead, and live off what they do.",
    [
        node(A, "sepulchral_might", "Sepulchral Might",
             "Increases your Stamina by 2% and your spell power by 5 per "
             "rank.",
             0, 0, 5, {"stamina_pct": 2.0, "spell_power": 5},
             source="CoA: 'Increases your Stamina by 5%. Increases your spell "
                    "damage by an amount equal to 15% of the total of your "
                    "Raised minion's Stamina.' A stat conversion needs both "
                    "sides on the same character - the shared "
                    "STAT_CONVERSION maps in character.py have no minion "
                    "source - so the conversion lands as flat spell power."),
        node(A, "graverobber", "Graverobber",
             "Reduces the Life Force cost of your abilities by 2% per rank.",
             0, 1, 5, {"all_ability_cost_pct": 0.02},
             source="CoA: 'Reduces the mana cost and cast time of your Raise "
                    "and Animate spells by -30%.' Nothing groups abilities "
                    "into CoA's Raise/Animate schools, so the reduction is "
                    "general and much smaller per rank."),
        node(A, "scourge_disciple", "Scourge Disciple",
             "Increases your haste by 1 per rank.",
             0, 2, 5, {"haste": 1.0},
             source="CoA: 'Each active Skeletal Archer now increases your "
                    "haste by 5%.' Archers are AoE damage here rather than "
                    "countable bodies, so the haste is unconditional. Haste "
                    "is third in this spec's stat priority."),
        node(A, "runic_animation", "Runic Animation",
             "Reduces the cooldown of Animate: Skeletal Archers by 5% per "
             "rank.",
             0, 3, 5,
             {"ability_necromancer_animate_skeletal_archers_cooldown_pct": 0.05},
             source="CoA: 'Reduces the cooldown of Animate: Skeletal Archers "
                    "and Command: Hook by -20%.' Archers is the cast this "
                    "spec presses on cooldown ('rotate RP into Animate: "
                    "Skeletal Archers ... on cooldown to keep bodies on the "
                    "pack'), so it gets the node."),

        node(A, "bone_king", "Bone King",
             "Your area spells have a 20% chance per rank to cast a free "
             "Lichfrost.",
             1, 0, 3, {}, connect=["sepulchral_might"],
             proc={"trigger": "on_damage_cast", "chance": 20, "icd": 1,
                   "ability_filter": ["necromancer_corpse_explosion",
                                      "necromancer_march_of_the_dead",
                                      "necromancer_animate_skeletal_archers"],
                   "cast_ability": "necromancer_lichfrost"},
             source="CoA: 'Bone King procs free instant Lichfrost or Blight' "
                    "- 'Casting Command spells now has a 15% chance to make "
                    "your next Lichfrost within 5 seconds instant cast.' "
                    "cast_ability fires the real ability for free, which is "
                    "closer to CoA's intent than a cast-time reduction would "
                    "be in a turn engine."),
        node(A, "forbidden_technique", "Forbidden Technique",
             "Reduces the cooldown of Animate: Plaguefather by 6% per rank.",
             1, 1, 3,
             {"ability_necromancer_animate_plaguefather_cooldown_pct": 0.06},
             connect=["graverobber"],
             source="CoA: 'Forbidden Technique shortens Animate cooldowns' - "
                    "'Casting Command spells now reduces the cooldown of your "
                    "Animates by -1 sec.' A cooldown key names one ability, "
                    "so it names the Animate the rotation leans on hardest "
                    "after the Archers."),
        node(A, "summoning_adept", "Summoning Adept",
             "Increases your minion's health by 4% per rank.",
             1, 2, 5, {"pet_health": 0.04}, connect=["scourge_disciple"],
             source="CoA's Summoning Adept/Expert/Prodigy line all read "
                    "'Increases your maximum Life Force by 1' - a bigger "
                    "minion budget. life_force_max is the key for that and "
                    "tools/audit_talents.py does not list it as live (see "
                    "module docstring), and only one pet can be active at a "
                    "time regardless, so a wider budget becomes a tougher "
                    "minion."),
        node(A, "skeletal_artillery", "Skeletal Artillery",
             "Increases the damage of Animate: Skeletal Archers by 5% per "
             "rank.",
             1, 3, 5,
             {"ability_necromancer_animate_skeletal_archers_damage": 0.05},
             connect=["runic_animation"],
             source="CoA: 'Your Animate: Skeletal Archers now summons 1 "
                    "additional Skeletal Archer.' More archers firing into "
                    "the same pack is more damage from the same cast."),

        node(A, "ghoul_mastery", "Ghoul Mastery",
             "Increases your minion's damage by 5% per rank.",
             2, 0, 3, {"pet_damage": 0.05}, connect=["bone_king"],
             source="CoA: 'Damage dealt by your Ghouls now has a 15% chance "
                    "to transform them into a Frenzied Ghoul, increasing "
                    "haste by 40% for 10 seconds.' A Pet has no proc system "
                    "and reads only pet_damage/pet_health/pet_armor off its "
                    "owner, so a haste frenzy becomes flat damage."),
        node(A, "anti_magic_shell", "Anti-Magic Shell",
             "Increases your minion's armor by 6% per rank.",
             2, 1, 3, {"pet_armor": 0.06}, connect=["forbidden_technique"],
             source="CoA: 'When you summon a Raised minion, it now raises "
                    "with a shield absorbing Magic damage equal to 40% of "
                    "their maximum health.' No absorb shields and no pet "
                    "magic resistance key; pet_armor is the third and last of "
                    "the owner talent keys a Pet reads, also a FRACTION."),
        node(A, "vampiric_aura", "Vampiric Aura",
             "Your damage spells have a 33% chance per rank to heal you for "
             "10% of the damage dealt.",
             2, 2, 3, {}, connect=["summoning_adept"],
             proc={"trigger": "on_damage_cast", "chance": 33, "icd": 1,
                   "leech_pct": {"pct": 0.10}},
             source="CoA class tree: 'While you are below 50% health, your "
                    "Undead minions now heal you for 10% of their damage "
                    "dealt.' A pet's damage is not a proc trigger on its "
                    "owner and there is no health condition on leech_pct, so "
                    "it fires off the Necromancer's own casts. This is the "
                    "spec's real sustain - CoA: 'There is no heal button here "
                    "and it does not need one.'"),
        node(A, "mindless_fury", "Mindless Fury",
             "Your casts have a 20% chance per rank to increase your haste by "
             "8 for 3 turns.",
             2, 3, 5, {}, connect=["skeletal_artillery"],
             proc={"trigger": "on_cast", "chance": 20, "icd": 1,
                   "apply_effect": {
                       "effect_id": "necromancer_mindless_fury",
                       "name": "Mindless Fury",
                       "effect_type": "buff",
                       "duration": 3,
                       "stat_mods": {"haste": 8.0},
                       "on_target": False}},
             source="CoA: 'Casting Animate or Command spells now increases "
                    "your haste by 1% for 10 seconds, stacking 5 times.' "
                    "Stacks are not expressible on a synthetic talent proc "
                    "effect, so the five-stack ceiling arrives as one larger "
                    "buff at a chance."),

        node(A, "flesh_symbiosis", "Flesh Symbiosis",
             "Increases your Armor by 3% and your magic resistance by 20 per "
             "rank.",
             3, 0, 3, {"armor_pct": 3.0, "magic_resistance": 20},
             connect=["ghoul_mastery"],
             source="CoA: 'Each Abomination or Decaying Colossus active now "
                    "increases your total Armor and magic resistance by 30% "
                    "and causes you to periodically regenerate 2% maximum "
                    "health every 5 sec.' Nothing counts active Abominations "
                    "and there is no periodic self-regen hook, so the armour "
                    "and resistance are unconditional and far smaller. NOTE "
                    "armor_pct is PERCENT POINTS (divided by 100), unlike the "
                    "pet_* fractions two tiers up."),
        node(A, "plague_horde", "Plague Horde",
             "Your damage spells have a 20% chance per rank to smear Zombie "
             "Plague on the target.",
             3, 1, 3, {}, connect=["anti_magic_shell"],
             proc=disease_proc(20, 40, "zombie_plague", "Zombie Plague",
                               icd=1),
             source="CoA: 'Damage dealt by your Undead minions now has a 10% "
                    "chance to cast Plague Horde on themselves ... and emit "
                    "Zombie Plague, dealing SP Plague damage to their "
                    "target.' A pet's hit cannot trigger an owner proc, so "
                    "the Necromancer emits it. Plague is Shadow here, per "
                    "CoA's own 'shadow SP Plague damage' wording."),
        node(A, "crypt_keeper", "Crypt Keeper",
             "Increases the damage your area effects deal by 8% per rank.",
             3, 2, 3, {"aoe_damage": 0.08}, connect=["vampiric_aura"],
             source="CoA: 'Your Crypt Swarm now bounces to 2 additional "
                    "nearby enemies, at 30% reduced value per enemy struck.' "
                    "Crypt Swarm is single-target here, so the bounce lands "
                    "on the Animate line, which is where this spec's area "
                    "damage actually is."),
        node(A, "unrelenting", "Unrelenting",
             "Increases the damage of Crypt Swarm by 6% per rank.",
             3, 3, 2, {"ability_necromancer_crypt_swarm_damage": 0.06},
             connect=["mindless_fury"],
             source="CoA: 'Reduces the channel time of your Crypt Swarm by "
                    "-25%.' A quarter off a channel is a quarter more damage "
                    "per turn spent on it, and Crypt Swarm is where this "
                    "spec's Life Force comes from."),

        node(A, "army_of_the_dead", "Army of the Dead",
             "Increases your minion's health by 5% per rank.",
             4, 0, 3, {"pet_health": 0.05}, connect=["flesh_symbiosis"],
             source="CoA: 'While only 1 Abomination is active, the critical "
                    "strike chance of your Ghouls is increased by 10% and "
                    "haste by 10%.' Pet crit and pet haste are not keys a Pet "
                    "reads; pet_health is, and CoA's own weakness list says "
                    "'AoE cleave or CC that kills the pets takes your damage "
                    "and your self-healing with them'."),
        node(A, "underking", "Underking",
             "Reduces the cooldown of Animate: Tomb King by 2 turns.",
             4, 1, 1, {"ability_necromancer_animate_tomb_king_cooldown": 2},
             connect=["plague_horde"],
             source="CoA: 'Casting Command spells now grants you a stack of "
                    "Underking ... At 10 stacks, the cooldown of Animate: "
                    "Tomb King, Animate: Bone Wraith or Animate: Plaguefather "
                    "is reduced by -15 sec at random.' No stack counter and no "
                    "random pick, so it is a flat reduction on the one the "
                    "rotation wants up permanently ('Keep Tomb King up')."),
        node(A, "long_march", "Long March",
             "Reduces the cooldown of March of the Dead by 8% per rank.",
             4, 2, 3,
             {"ability_necromancer_march_of_the_dead_cooldown_pct": 0.08},
             connect=["crypt_keeper"],
             source="CoA: 'Removes the cooldown from March of the Dead, but "
                    "gives it a 1 sec cast time.' talented_cooldown floors "
                    "every cooldown at 1 turn, so removing it outright is "
                    "impossible by design - eight abilities once went "
                    "spammable that way. A reduction instead, with no cast "
                    "time to trade for it."),

        node(A, "chomp", "Chomp",
             "Your critical strikes have a 25% chance per rank to tear 90 "
             "extra damage out of the target.",
             5, 0, 3, {}, connect=["army_of_the_dead"], total_slots=3,
             proc={"trigger": "on_crit", "chance": 25, "icd": 1,
                   "damage_flat": 90},
             source="CoA: 'Critical strikes dealt by your Abominations and "
                    "Decaying Collosi now Chomp your target, dealing SP "
                    "damage to them.' A pet's crit is not an owner proc "
                    "trigger, so the Necromancer's own crits do the biting."),
        node(A, "corpse_wagon", "Corpse Wagon",
             "Increases all damage you deal by 2% per rank.",
             5, 1, 2, {"all_damage": 0.02}, connect=["underking"],
             total_slots=3,
             source="CoA: 'Increases all damage dealt by party and raid "
                    "members by 3% ... In addition, increases the damage of "
                    "Corpse Explosion by 25%.' The party aura is the ability "
                    "of the same name; a talent only reads off its own "
                    "character, so this is the self share."),
        node(A, "plague_protection", "Plague Protection",
             "Reduces all damage you take by 2% per rank.",
             5, 2, 2, {"damage_taken_pct": -0.02}, connect=["long_march"],
             total_slots=3,
             source="CoA: 'Increases the effectiveness of your Wards by 25%.' "
                    "Wards here are Fetid Ward and Anti-Magic Shell, both "
                    "defensive, and there is no ability-effectiveness key, so "
                    "the node is flat mitigation. NOTE damage_taken_pct is a "
                    "FRACTION as a talent and also as a buff - one of the few "
                    "keys where the two conventions agree."),

        node(A, "master_animator", "Master Animator",
             "Whatever you raise comes up bigger, meaner and harder to put "
             "back down.",
             6, 0, 1, {"pet_damage": 0.15, "pet_health": 0.15,
                       "pet_armor": 0.15},
             connect=["chomp", "corpse_wagon", "plague_protection"],
             total_slots=1,
             source="Capstone. CoA's own tier-6 Master Animator is 'Increases "
                    "your maximum Life Force by 1' - one more minion. The key "
                    "for that pool is not available to a talent here (see "
                    "module docstring) and only one pet can be active at a "
                    "time anyway, so the capstone spends itself on the minion "
                    "you do have, across all three keys a Pet reads. CoA "
                    "rates this spec Arena A / BG A on exactly this: "
                    "'Permanent Raise: Ghoul pets stack with temporary "
                    "Animate pets ... Several bodies soaking and dealing "
                    "damage at once covers for bringing no hard CC.'"),
    ],
    "Built from reference/coa_sidekick/SPEC_necromancer__animation.txt and "
    "the 42 'animation' nodes in reference/coa_sidekick/talents/"
    "necromancer.json. CoA: 'You play less like a spellcaster and more like a "
    "one-person raid group', and it is the recommended levelling spec because "
    "'An undead army tanks and kills for you while you stay at range'. The "
    "engine allows exactly ONE active pet (Character.summon_pet replaces "
    "active_pet) and no new pet templates, so CoA's stacked army is split in "
    "two here: the one real minion, which this tree makes as strong as the "
    "three live pet keys allow (Summoning Adept, Ghoul Mastery, Anti-Magic "
    "Shell, Army of the Dead, Master Animator), and the temporary Animates, "
    "which are area-damage abilities rather than bodies. Stat priority is "
    "Spell Hit > Spell Power > Haste > Intellect > Crit.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    ability_doc = {
        "class": "Necromancer",
        "_source_note": __doc__.strip().split("\n\n")[1].replace("\n", " "),
        "abilities": ABILITIES,
    }

    targets = [
        (ROOT / "data/abilities/necromancer.json", ability_doc),
        (ROOT / "data/talents/necromancer_death.json", DEATH),
        (ROOT / "data/talents/necromancer_rime.json", RIME),
        (ROOT / "data/talents/necromancer_animation.json", ANIMATION),
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
