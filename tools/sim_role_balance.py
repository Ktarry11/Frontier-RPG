#!/usr/bin/env python3
"""Balance tanks against tanks and healers against healers, on the axes their role is judged by.

    PYTHONPATH=. python3 tools/sim_role_balance.py [--role tank] [--level 60] [--fights 8]

Kyle, 2026-10-28: "Keep in mind each tank will be better at different things. same with healers etc."
and "think of classic healers and tanks."

WHY THIS IS A SECOND TOOL AND NOT MORE COLUMNS ON THE FIRST ONE. sim_class_balance.py asks one
question - can this class kill a creature a few levels above it - and that is the right question for
damage specs and a meaningless one for the other two roles. A tank that kills slowly is not broken, a
healer that kills slowly is doing its job. Measured on kill speed, every tank and healer in the game
looks bad, which is how you end up "fixing" things that were never wrong.

BALANCED DOES NOT MEAN IDENTICAL, which is the whole point of the instruction. Classic's tanks were
not interchangeable: the Protection Warrior held the most threat and mitigated the most, the
Protection Paladin gave up single-target threat for area threat and self-healing, and the bear gave
up blocking for raw health and armour. Its healers were the same - Holy Priest the efficient
all-rounder, Discipline preventing damage rather than repairing it, Resto Druid working through
heals-over-time, Resto Shaman healing groups, Holy Paladin the single-target specialist. So this
tool does not look for equal numbers. It looks for three specific failures:

    NOT VIABLE     - cannot do its job at all
    WORST AT ALL   - behind every peer on every axis, with no compensating strength
    BEST AT ALL    - ahead of every peer on every axis, so nobody else has a reason to exist

Anything else - ahead here, behind there - is the design working.

SPECS ARE REALLY APPLIED. A character is built, then up to its level's talent budget is invested into
that spec's own tree, deepest tier first, the way a player spends them. A level 60 has 56 points
against a tree that can absorb 63, so no build is complete and the choices show. Without this the
tool would be comparing classes, and a class is not a role - Warrior Protection and Warrior Fury
share every base stat and nothing else.
"""
import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: spec -> role. The 25 specs a recruit exists for are ground truth from their gear_theme in
#: data/npcs/recruits.json; the other 31 are read off each tree's own description in data/talents.
#: Roles are the four the game already uses for recruit gear themes, not a new vocabulary.
SPEC_ROLES = {
    # ---- tanks: block-and-shield chassis, or the armour-and-health kind
    "warrior_protection": "tank", "paladin_protection": "tank", "cultist_dreadnought": "tank",
    "primalist_mountain_king": "tank", "venomancer_fortitude": "tank",
    "starcaller_moon_guard": "tank", "sun_cleric_seraphim": "tank",
    # DRUID FERAL IS THE DRUID TANK AND THE DRUID MELEE, exactly as Classic's Feral tree was. Its
    # 24 nodes carry both halves - Thick Hide, Dire Bear Form, Natural Reaction, Protector of the
    # Pack and Improved Bear Form on the bear side, Shred, Rake, Ferocious Bite and King of the
    # Jungle on the cat side - with require_form splitting them. Filing it under melee_dps alone
    # left the tank audit with no druid in it at all, which Kyle spotted immediately.
    "druid_feral": ("tank", "melee_dps"),
    # TINKER MECHANICS IS NOT A TANK. Its description says it "dons a powered Mechsuit to soak
    # damage and hit hard" and I read the soaking half and filed it as a tank. Kyle: "tinkerer is
    # NOT a tank, it has DPS specs or healer." Mechanics is the melee one, Demolition the ranged
    # one, Invention the healer.
    "tinker_mechanics": "melee_dps",
    # ---- healers, including the hybrids that heal by dealing damage or by support
    "priest_holy": "healer", "priest_discipline": "healer", "paladin_holy": "healer",
    "druid_restoration": "healer", "shaman_restoration": "healer",
    "starcaller_moon_priest": "healer", "sun_cleric_blessings": "healer",
    "tinker_invention": "healer",
    "venomancer_vizier": "healer", "cultist_heretic": "healer",
    # NOT healers, corrected 2026-10-28 against reference/coa_sidekick. I had
    # classified both of these myself, from tree descriptions, and the real
    # CoA pages disagree:
    #   stormbringer_wind     "RANGED DPS / SUPPORT ... Closest to
    #                         Augmentation Evoker" - it has one heal ability
    #                         in the whole kit and read 0 healing per turn
    #                         because it is not a healer, not because it is
    #                         broken.
    #   primalist_grovekeeper "SUPPORT ... Closest to Mistweaver Monk in
    #                         Fistweaving mode" - it heals by punching
    #                         things, which a static heal-the-patient
    #                         measurement cannot see at all.
    # Two of the five "broken healers" I was about to fix were specs sitting
    # a test they were never meant to take.
    "stormbringer_wind": "ranged_dps",
    "primalist_grovekeeper": ("melee_dps", "healer"),
    # ---- melee damage
    "warrior_fury": "melee_dps", "warrior_arms": "melee_dps", "rogue_combat": "melee_dps",
    "rogue_assassination": "melee_dps", "rogue_subtlety": "melee_dps",
    "shaman_enhancement": "melee_dps", "stormbringer_lightning": "melee_dps",
    "runemaster_riftblade": "melee_dps", "runemaster_engravement": "melee_dps",
    "cultist_godblade": "melee_dps",
    "paladin_retribution": "melee_dps", "primalist_wildwalker": "melee_dps",
    "starcaller_warden": "melee_dps", "sun_cleric_valkyrie": "melee_dps",
    "venomancer_stalking": "melee_dps",
    # ---- ranged and caster damage
    "hunter_marksmanship": "ranged_dps", "hunter_beast_mastery": "ranged_dps",
    "hunter_survival": "ranged_dps", "mage_fire": "ranged_dps", "mage_frost": "ranged_dps",
    "mage_arcane": "ranged_dps", "warlock_demonology": "ranged_dps",
    "warlock_affliction": "ranged_dps", "warlock_destruction": "ranged_dps",
    "druid_balance": "ranged_dps", "priest_shadow": "ranged_dps",
    "shaman_elemental": "ranged_dps", "cultist_corruption": "ranged_dps",
    "primalist_geomancy": "ranged_dps", "runemaster_glyphic": "ranged_dps",
    "starcaller_sentinel": "ranged_dps", "stormbringer_maelstrom": "ranged_dps",
    "sun_cleric_piety": "ranged_dps", "tinker_demolition": "ranged_dps",
    "venomancer_venom": "ranged_dps",
    # ---- Guardian, authored 2026-10-28. CoA: "a tanking-focused warrior
    # class with the best damage mitigation in the game". Vanguard is the
    # Protection Warrior analog; Inspiration is melee support ("an
    # Augmentation Evoker that decided to also gear like a Protection
    # Warrior"); Gladiator is Prot played offensively.
    "guardian_vanguard": "tank",
    "guardian_inspiration": "melee_dps",
    "guardian_gladiator": "melee_dps",
    # ---- THE THIRTEEN CLASSES ADDED AFTER THIS TABLE WAS WRITTEN.
    # 38 real talent trees had no role at all, so every balance run since
    # has measured 59 specs out of 97 and silently left the rest out. Six
    # of the missing ones are TANKS and three are HEALERS, which is most of
    # what a role audit is for.
    #
    # ROLES TAKEN FROM reference/coa_sidekick, NOT from the tree
    # descriptions. Reading descriptions is how I got Tinker Mechanics,
    # Stormbringer Wind and Primalist Grovekeeper wrong, all three of which
    # Kyle corrected - and two of the five "broken healers" in the 28 Oct
    # audit turned out to be specs sitting a test they were never meant to
    # take. Each SPEC_*.txt states its role outright; that is the ground
    # truth and this table now just copies it.
    #
    # One CoA spec is deliberately absent: venomancer_rot. The reference
    # has a page for it and the game has no such talent tree, so adding it
    # would put a role on a spec nobody can play.
    "barbarian_ancestry": "melee_dps", "barbarian_brutality": "melee_dps",
    "barbarian_headhunting": "ranged_dps",
    "bloodmage_accursed": "melee_dps", "bloodmage_eternal": "tank",
    "bloodmage_fleshweaver": "ranged_dps", "bloodmage_sanguine": "ranged_dps",
    "chronomancer_artificer": "ranged_dps", "chronomancer_infinite": "ranged_dps",
    "chronomancer_time": "healer",
    "felsworn_infernal": "ranged_dps", "felsworn_slayer": "melee_dps",
    "felsworn_tyrant": "tank",
    "knight_of_xoroth_defiance": "tank", "knight_of_xoroth_hellfire": "melee_dps",
    "knight_of_xoroth_war": "melee_dps",
    "necromancer_animation": "ranged_dps", "necromancer_death": "ranged_dps",
    "necromancer_rime": "ranged_dps",
    "pyromancer_draconic": "ranged_dps", "pyromancer_flameweaving": "healer",
    "pyromancer_incineration": "ranged_dps",
    "ranger_archery": "ranged_dps", "ranger_brigand": "melee_dps",
    "ranger_farstrider": "ranged_dps",
    "reaper_domination": "tank", "reaper_harvest": "melee_dps",
    "reaper_soul": "melee_dps",
    "templar_crusader": "melee_dps", "templar_oathkeeper": "tank",
    "templar_zealot": "melee_dps",
    "witch_doctor_brewing": "healer", "witch_doctor_shadowhunting": "ranged_dps",
    "witch_doctor_voodoo": "ranged_dps",
    "witch_hunter_black_knight": "tank", "witch_hunter_boltslinger": "ranged_dps",
    "witch_hunter_houndmaster": "ranged_dps", "witch_hunter_inquisition": "melee_dps",
}

#: THE FORM IS PART OF THE SPEC. A feral druid measured out of Bear Form has the armour of a
#: caster, and Cultist Dreadnought's whole chassis is Void Monstrosity (armour 160, stamina 35,
#: -10% damage taken). Best first - Dire Bear before Bear - and only if the character can use it.
ROLE_FORMS = {
    "tank": ["dire_bear", "void_monstrosity", "bear", "beetle"],
    "melee_dps": ["cat", "spider"],
    "healer": ["tree_of_life", "vizier_form"],
    "ranged_dps": ["moonkin", "shadowform", "weaver"],
}

#: Which talent effects matter for which role, so a dual-role tree is built the way a player
#: building for that role would build it rather than bottom-up and undifferentiated.
ROLE_EFFECTS = {
    "tank": ("armor", "dodge", "block", "max_health", "damage_taken", "threat", "stamina",
             "parry", "shield"),
    "healer": ("healing", "heal", "mana", "spirit", "intellect"),
    "melee_dps": ("damage", "crit", "attack_power", "strength", "agility", "haste"),
    "ranged_dps": ("damage", "crit", "spell_power", "intellect", "haste"),
}


def precast_stances(char, engine):
    """Put one stance per exclusive group up before measuring, out of combat.

    THE TANK AND HEALER SIMS HAD NO STANCE HANDLING AT ALL. Neither
    tank_axes nor healer_axes ever cast a setup buff, so every spec was
    measured with its always-on toggle switched off: a Protection Warrior
    with no stance, a Protection Paladin with no Seal, a Resto Shaman with no
    weapon imbue, a Chronomancer healer with no Aeon, a Druid that never
    shifted. For a tank that is not a rounding error - a defensive stance or
    presence is a core slice of its mitigation, which is the exact axis
    tank_axes exists to measure.

    The class sim learned this the hard way on 29 Oct: casting these INSIDE
    the fight charged a turn per exclusive group, which taxed the classes
    with the richest stance systems hardest. They are pre-pull buffs with
    60-turn durations, so they go up before measurement starts and cost
    nothing - and resources are topped back up afterwards, since a pre-pull
    buff is paid for out of combat.

    One per exclusive_group, not one in total: a class can hold a Seal and a
    Presence and an Aspect at the same time, and they are different groups.
    """
    learned = char.get_learned_abilities()
    needed_forms = set()
    for a in learned:
        rf = getattr(a, "requires_form", None)
        if rf:
            needed_forms.update(rf if isinstance(rf, (list, tuple)) else [rf])
    setup = [a for a in learned
             if getattr(a, "effect_type", "") == "buff"
             and getattr(a, "target_type", None) in (None, "self")
             and (getattr(a, "exclusive_group", None)
                  or getattr(a, "shapeshift_form_id", None) in needed_forms)]
    for _pass in range(len(setup)):
        up = set()
        mine = {getattr(fx, "effect_id", None) for fx in getattr(char, "active_effects", [])}
        names = {getattr(fx, "name", None) for fx in getattr(char, "active_effects", [])}
        for b in setup:
            if b.ability_id in mine or b.name in names:
                up.add(getattr(b, "exclusive_group", None)
                       or getattr(b, "shapeshift_form_id", None) or b.ability_id)
        progressed = False
        for b in setup:
            if b.ability_id in mine or b.name in names:
                continue
            key = (getattr(b, "exclusive_group", None)
                   or getattr(b, "shapeshift_form_id", None) or b.ability_id)
            if key in up:
                continue
            if engine.execute_ability(char, b.ability_id, char)[0]:
                up.add(key)
                progressed = True
        if not progressed:
            break
    char.current_health = char.health
    if getattr(char, "mana", 0):
        char.current_mana = char.mana
    return setup


#: What a tank is hit by while being measured: the hardest thing in the game at its own level.
TANK_ATTACKER = "elemental_caster"
TANK_PHYSICAL = "beast_large"

TICK = 0.05
MAX_TICKS = 20000

#: Healer turns in the measurement window. Replaced a `casts >= 30` cap on
#: 29 Oct. Capping CASTS made the window a different length for every spec -
#: a direct healer casting every turn stopped at turn 30, while a HoT spec
#: that holds its turn while its HoTs roll needed 60+ turns to reach 30 casts
#: and, once every heal it owns was already rolling, never got there at all:
#: venomancer_vizier ran to MAX_TICKS and reported 0 healing/turn against 402
#: healing/cast, which is the same healing divided by a denominator 20000
#: long. A fixed turn budget gives every spec the same denominator, which is
#: the only way the throughput column means anything across the table.
TURN_BUDGET = 40


def roles_of(spec):
    r = SPEC_ROLES[spec]
    return (r,) if isinstance(r, str) else tuple(r)


def display_names():
    """The real class names, from the engine. Not derived, looked up."""
    import re
    text = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    block = text.split("class_stats = {", 1)[1].split("\n        }", 1)[0]
    return re.findall(r'^\s*"([^"]+)":\s*\{\s*#?', block, re.M)


def class_of(spec):
    """'sun_cleric_seraphim' -> 'Sun Cleric'. Longest matching class slug wins, so multi-word
    class names are not split at the wrong underscore.

    THE NAME IS LOOKED UP, NOT TITLE-CASED. This returned
    slug.replace("_", " ").title(), which gives 'Knight Of Xoroth' with a
    capital O where the game's own class is 'Knight of Xoroth'. Nothing
    complained, because three separate lookups all fail SOFT on an unknown
    class name:

      Character.__init__      falls back to default stats - the mis-cased
                              Knight read strength 39 instead of 53 and
                              492 health instead of 412
      class_armor_map.get()   defaults to "cloth", so a PLATE tank was
                              measured in cloth and came out with 785
                              armour against Protection Warrior's 2763
      class_stat_template_map defaults to "int_caster", so its gear rolled
                              caster stats on top of that

    Knight of Xoroth is the only class in the game whose name contains a
    lowercase connector, so it is the only one title() corrupts - which is
    exactly why it survived: every other multi-word class (Witch Hunter,
    Sun Cleric, Witch Doctor) title-cases correctly and the bug looked like
    a balance result. It read as the worst tank in the game on effective
    HP, physical reduction, damage taken and turns alive, all four of them
    an artifact of one capital letter.
    """
    slugs = sorted((p.stem for p in (ROOT / "data/abilities").glob("*.json")),
                   key=len, reverse=True)
    real = {n.lower().replace(" ", "_"): n for n in display_names()}
    for slug in slugs:
        if spec.startswith(slug + "_"):
            if slug in real:
                return real[slug]
            raise KeyError(
                f"class slug {slug!r} (from spec {spec!r}) is not a class in "
                f"entities/character.py class_stats - fix the name rather than "
                f"letting it fall back to default stats and cloth gear")
    raise KeyError(f"no class owns spec {spec!r}")


def build(spec, level, gen, dress, role=None):
    """A character of this spec with its talents spent FOR THAT ROLE, its form on, and gear."""
    from entities.character import Character
    import inspect

    char = Character("Sim", class_of(spec), level)
    tree = char.talent_trees.get(spec)
    if tree is None:
        raise KeyError(f"{class_of(spec)} has no tree {spec!r}; has {list(char.talent_trees)}")

    budget = char.talent_points_available
    probe = tree.nodes[list(tree.nodes)[0]]
    takes_tree = "tree" in str(inspect.signature(probe.can_spend_point))
    spent = 0
    wanted = ROLE_EFFECTS.get(role or "", ())

    def relevant(node):
        """Does this node do anything the role cares about? Druid Feral holds a bear tank and a cat
        rogue in one tree, so spending bottom-up gives a build that is neither."""
        if not wanted:
            return True
        # A NODE THAT GRANTS AN ABILITY IS ALWAYS RELEVANT. The keyword match
        # below reads effect KEYS and the node name, and an unlock node's only
        # effect key is "unlock_ability" - so Druid Restoration's Swiftmend
        # (name "Swiftmend", effects {"unlock_ability": "druid_swiftmend"})
        # matched none of "healing/heal/mana/spirit/intellect", sorted last in
        # every tier, and never got bought on a 56-point budget. The spec was
        # being measured without its signature button. This is not a Druid
        # quirk: 325 nodes across 70 of the 97 trees unlock an ability this
        # way, so the bias ran through the tank table too. A tree only ever
        # unlocks abilities belonging to its own spec, so taking them is
        # always right; and because the climb phase SORTS by relevance rather
        # than excluding, this only stops them being deprioritised to never.
        if "unlock_ability" in (node.effects or {}):
            return True
        keys = " ".join((node.effects or {})).lower() + " " + (node.name or "").lower()
        return any(w in keys for w in wanted)

    def put(node):
        """Spend one point if allowed. Returns True if it landed."""
        nonlocal spent
        if spent >= budget:
            return False
        ok = node.can_spend_point(tree) if takes_tree else node.can_spend_point()
        if not ok or not node.spend_point():
            return False
        spent += 1
        return True

    # CLIMB FIRST, THEN FILL. The previous version walked up from the bottom taking max_points on
    # every role-relevant node, which is not how anyone builds and it silently truncated whole
    # trees: Guardian Vanguard's tiers 0-2 hold 53 points, so a 56-point budget was exhausted by
    # tier 3 and it never reached its threat talent OR its capstone. It read "threat +0%, best at
    # nothing but effective HP" - a conclusion about the harness, not the spec. Any tree with fat
    # lower tiers was being judged without its top half.
    #
    # A player spends the minimum needed to unlock the next tier, climbs to the capstone, then
    # spends what is left broadening the build. So: phase one buys the cheapest path upward,
    # preferring role-relevant nodes; phase two fills.
    max_tier = tree.get_max_tier()
    for tier in range(0, max_tier + 1):
        needed = tree.tier_requirements.get(tier + 1, 0) if tier < max_tier else 0
        ordered = sorted(tree.get_nodes_in_tier(tier), key=lambda n: not relevant(n))
        # enough to open the next tier, plus the capstone row itself
        for node in ordered:
            while spent < budget and (spent < needed or tier == max_tier):
                if not put(node):
                    break
            if tier < max_tier and spent >= needed:
                break

    # Phase two: broaden, bottom up, role-relevant first - the points a real build has left over.
    for tier in range(0, max_tier + 1):
        for node in sorted(tree.get_nodes_in_tier(tier), key=lambda n: not relevant(n)):
            while spent < budget:
                if not put(node):
                    break
    for sync in ("_sync_talent_procs", "_sync_talent_unlocked_abilities",
                 "_recalculate_derived_stats", "_refresh_ability_ranks"):
        if hasattr(char, sync):
            try:
                getattr(char, sync)()
            except Exception:                                   # noqa: BLE001
                pass
    dress(char, gen, level)

    # A SHIELD TANK NEEDS A SHIELD, and the generic gearing pass does not guarantee one - it asks
    # for an off_hand and takes whatever that class rolls. Block chance only exists with a shield
    # equipped, so without this the shield specs measured 0% block and their block talents did
    # nothing. Which specs count is read off the trees rather than hardcoded: a tree that spends
    # points on the `block` effect is a tree built around carrying one.
    if role == "tank" and char.get_talent_effect("block"):
        held = char.equipment.get_equipped("off_hand")
        if not held or not getattr(held, "block_value", 0):
            shield = gen.generate_weapon("off_hand", "shield", "str_physical", level, "rare")
            if shield is not None:
                char.inventory.append(shield)
                if not char.equip_item(shield) and shield in char.inventory:
                    char.inventory.remove(shield)

    for form in ROLE_FORMS.get(role or "", []):
        if hasattr(char, "can_use_form") and char.can_use_form(form):
            char.shift_form(form)
            # SHIFTING ZEROES THE RESOURCE POOL, and that is correct game
            # behaviour - Character.shift_form sets current_mana/rage/energy
            # to 0, matching WOTLK's "shifting resets your current resource".
            # It is wrong for a MEASUREMENT though. The harness shifts and
            # then immediately starts casting, so a healer in Tree of Life or
            # Vizier Form began every measurement at 0 mana and could never
            # cast a single spell: druid_restoration, primalist_grovekeeper,
            # venomancer_vizier and stormbringer_wind all read 0 healing per
            # turn, and cultist_heretic read 8. I nearly buffed four healers
            # that were never broken.
            #
            # A real player shifts and then regenerates before or during the
            # fight; what we want to know is steady-state capability, not the
            # single tick after a shift. So top every pool back up.
            break
    _fill_resources(char)
    return char, spent


#: Every resource pool a spec might spend from. The efficiency axis sums
#: across all of them because "healing per 100 mana" is the wrong question
#: for a spec that does not spend mana: Cultist Heretic funds its
#: damage-that-heals loop with INSANITY, so measuring only current_mana
#: reported 0 healing per 100 mana - "score zero where every peer scores
#: something" - for a spec whose efficiency is actually fine. Same trap
#: would catch any Rage or Energy healer added later.
RESOURCE_POOLS = (
    "current_mana", "current_energy", "current_rage", "current_focus",
    "current_insanity", "current_combo", "current_static", "current_runes",
    "current_souls", "current_felfury", "current_deathfire",
    "current_vitality", "current_solar_power", "current_life_force",
    "current_archery_points",
)


def _resource_snapshot(char):
    """Every resource pool's current value, for measuring spend per pool."""
    return {pool: getattr(char, pool, 0) or 0 for pool in RESOURCE_POOLS}


def _resource_spend(before, after):
    """Total DECREASE across pools, counted per pool.

    Per pool, and only decreases, because a builder/spender kit moves two
    pools in opposite directions in a single cast. Summing the pools into
    one number first - which is what the previous version of this did - let
    Cultist Heretic's Insanity GENERATION cancel its Mana cost, so the net
    came out at zero or positive and the spec read 0 healing per 100
    resource for the second time, by a different mistake than the first.
    """
    return sum(max(0, before.get(k, 0) - after.get(k, 0))
               for k in set(before) | set(after))


def _fill_resources(char):
    """Put every resource pool back to full before measuring.

    Used after a form shift (which deliberately zeroes them) and before each
    measured fight, so a spec is judged on what it can do rather than on
    whatever the harness left in its pool.
    """
    if hasattr(char, "mana"):
        char.current_mana = char.mana
    if hasattr(char, "max_energy"):
        char.current_energy = char.max_energy
    for pool, cap in (("current_rage", 100), ("current_focus", 100),
                      ("current_insanity", 100), ("current_combo", 100),
                      ("current_static", 100), ("current_runes", 100),
                      ("current_souls", 100), ("current_felfury", 100),
                      ("current_deathfire", 100), ("current_vitality", 100),
                      ("current_solar_power", 100), ("current_life_force", 100),
                      ("current_archery_points", 100)):
        if hasattr(char, pool):
            setattr(char, pool, cap)


def tank_axes(char, level, gen, dress, fights):
    """What a tank is actually for: not dying, and being the one that gets hit."""
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party

    learned = char.get_learned_abilities()
    rotation = [a for a in learned
                if getattr(a, "effect_type", "") in ("damage", "spell_damage", "spell_dot", "dot",
                                                      "damage_and_heal", "ranged_damage")]
    rotation.sort(key=lambda a: -(getattr(a, "effect_value", 0) or 0))

    # A TANK PRESSES ITS DEFENSIVE COOLDOWNS. This harness built the rotation
    # from offensive abilities only, so it never cast one - and a tank's
    # cooldowns are most of what a tank IS. Warrior's Shield Wall, Guardian's
    # Raise Shield and Brace and Bastion, Paladin's whole kit, and the Rock
    # Barrier and Earthen Avatar just authored for Mountain King were all
    # invisible to every tank measurement taken today. Mountain King read 5
    # turns alive while holding two unused cooldowns.
    #
    # Found by adding two abilities, verifying by hand that they cast and
    # that Rock Barrier takes armour 164 -> 199, and then watching the sim
    # report no change at all.
    #
    # Picked by what the buff DOES rather than by name: a self-buff carrying
    # any mitigation or avoidance stat_mod. The engine refuses one already
    # running or still on cooldown, so "cast it when available" needs no
    # cooldown bookkeeping here - exactly how the offensive rotation works.
    MITIGATION_KEYS = {"damage_taken_pct", "physical_damage_taken_pct",
                       "magic_damage_taken_pct", "spell_damage_taken_pct",
                       "armor_pct", "armor", "block", "dodge", "parry",
                       "block_value_pct", "max_health_pct"}
    # AN ABSORB SHIELD IS MITIGATION, and this filter could not see one.
    # Picking defensives by their stat_mods alone missed every buff whose
    # whole job is a shield, because an absorb carries no stat_mods at all -
    # twelve of them across the game, including BOTH of Cultist
    # Dreadnought's (Dreadnought Shield 0.25 and Eldritch Bastion 0.35) and
    # Templar Oathkeeper's Tome of Light at 0.40 of max health. The 28 Oct
    # audit called Dreadnought "zero block" and "best at nothing" while it
    # was holding two unused shields, which is the same failure as Mountain
    # King reading 5 turns alive with two unused cooldowns - the one this
    # branch was written to fix. Fixed one layer too shallow the first time.
    def mitigation_weight(a):
        mods = getattr(a, "stat_mods", {}) or {}
        w = sum(abs(v) for k, v in mods.items() if k in MITIGATION_KEYS)
        # absorb_pct_max_health is a FRACTION of max health (banded
        # 0.06-0.40 across the game); x100 puts it on the same scale as the
        # percent-point mitigation keys so the sort compares like with like.
        w += (getattr(a, "absorb_pct_max_health", 0) or 0) * 100
        w += (getattr(a, "absorb", 0) or 0) / 20.0
        return w

    defensives = [a for a in learned
                  if getattr(a, "effect_type", "") == "buff"
                  and getattr(a, "target_type", None) in (None, "self")
                  and mitigation_weight(a) > 0]
    # Strongest first, by how much mitigation it actually carries.
    defensives.sort(key=lambda a: -mitigation_weight(a))

    #: At most one defensive cooldown every this many turns - see the
    #: rationing note in the turn loop. Mirrors healer_axes' HEAL_EVERY.
    DEFEND_EVERY = 4

    taken = []
    for template in (TANK_ATTACKER, TANK_PHYSICAL):
        for _ in range(max(1, fights // 2)):
            char.current_health = char.health
            enemy = Monster("hitter", template, level)
            engine = CombatEngine(char, enemy, party=Party(char))
            precast_stances(char, engine)
            enemy.current_health = 10 ** 6          # measure survival, not the tank's damage
            turns, samples = 0, []
            last_defensive = -DEFEND_EVERY     # first defensive is allowed immediately
            for _ in range(MAX_TICKS):
                engine.update(TICK)
                if not engine.is_active:
                    break
                actor = engine.current_actor
                if actor is None:
                    continue
                if actor is char:
                    # A TANK THAT STANDS STILL IS NOT A TANK, and measuring one that way hides
                    # half its kit. Starcaller Moon Guard's mitigation buffs trigger on
                    # on_damage_cast - Guarded by the Moon fires at 100% when it casts Starburst
                    # or Starsweep - and Dreadnought's Void-Enhanced Shield triggers on_cast. With
                    # the tank only defending, none of that ever fired and both read as having no
                    # mitigation beyond their armour. It holds threat by attacking now, same as a
                    # real one, and the damage-taken numbers include whatever its rotation earns.
                    acted = False
                    # DEFENSIVES HAVE TO BE RATIONED, exactly like the heals in
                    # healer_axes. "Cast one when it is available" looked safe
                    # because the engine refuses an ability on cooldown - but
                    # several defensives have a cooldown of ZERO (Primalist's
                    # Boon of the Turtle: cd 0, duration 30), so the tank
                    # re-cast one every single turn, never attacked, took
                    # almost nothing and the fight never ended. Mountain King
                    # and Moon Guard read 940 and 964 turns alive at 1 damage
                    # taken per turn. That measured the loop, not the spec.
                    #
                    # A real tank spends a cooldown and then goes back to work.
                    # One defensive every DEFEND_EVERY turns at most, and never
                    # one already running on it.
                    may_defend = (turns - last_defensive) >= DEFEND_EVERY
                    live_buffs = {getattr(fx, "effect_id", None)
                                  for fx in getattr(char, "active_effects", [])}
                    live_names = {getattr(fx, "name", None)
                                  for fx in getattr(char, "active_effects", [])}
                    if may_defend:
                        for ability in defensives:
                            if ability.ability_id in live_buffs or ability.name in live_names:
                                continue
                            if engine.execute_ability(char, ability.ability_id, char)[0]:
                                acted = True
                                last_defensive = turns
                                break
                    if not acted:
                        for ability in rotation:
                            if engine.execute_ability(char, ability.ability_id, enemy)[0]:
                                acted = True
                                break
                    if not acted:
                        engine.execute_defend(char)
                    # SELF-HEALING CANNOT BE SEPARATED OUT HERE, and trying to was a mistake
                    # worth leaving a note about. Primalist Mountain King heals on_damage_taken,
                    # which fires inside the creature's own turn - the hit and the heal resolve
                    # together, so all that is observable is the net. A separate "self-heal/turn"
                    # axis read 0 for it while its damage taken dropped from 207 to 121, which is
                    # the self-healing, just counted in the other column. "net dmg/turn" below is
                    # already net of every heal, absorb and proc the spec has, which is the honest
                    # measure and the one a tank is judged by anyway.
                    continue
                # ABSORBED DAMAGE IS DAMAGE TAKEN, counted against the
                # shield instead of the health bar. This loop resets
                # current_health to full every turn so each swing is
                # measured in isolation - but it does NOT reset status
                # effects, so an absorb shield soaks hit after hit against
                # a pool that never visibly drains, and `before -
                # current_health` reads 0 every single turn.
                #
                # That produced reaper_domination at 0.01 damage a turn and
                # 195,300 turns alive the moment absorb shields were added
                # to the defensive rotation - immortality invented by the
                # harness, from a change made two hours earlier to fix the
                # opposite problem. A shield is a finite resource being
                # spent, so spending 500 of it is 500 damage the tank had
                # to pay for, and it belongs in the average.
                def absorb_pool():
                    return sum(getattr(fx, "absorb", 0) or 0
                               for fx in getattr(char, "active_effects", []))

                before = char.current_health
                shield_before = absorb_pool()
                engine.execute_monster_action()
                hit = (before - char.current_health) + (shield_before - absorb_pool())
                # EVERY SWING COUNTS, INCLUDING THE ONES THAT DEALT NOTHING.
                # This was `if hit > 0`, which dropped avoided swings from the
                # sample entirely - so the mean below was damage per LANDED
                # hit, not per turn, and "turns alive" (health / that) gave an
                # avoidance tank no credit whatsoever for avoiding anything.
                # Primalist Mountain King avoids roughly 70% of physical
                # swings and every one of them was discarded, which
                # systematically penalised exactly the specs these two axes
                # were being used to judge. A turn in which the tank took zero
                # damage is a turn it survived, so it belongs in the average.
                samples.append(hit)
                char.current_health = char.health
                turns += 1
                if turns >= 25:
                    break
            if samples:
                taken.append(statistics.mean(samples))
    dpt = statistics.mean(taken) if taken else 0
    reduction = char.get_physical_reduction_percent() / 100.0
    magic_cut = -(char.get_talent_effect("magic_damage_taken_pct")
                  + char.get_talent_effect("spell_damage_taken_pct")) * 100
    magic_cut += char.get_magic_reduction_percent()
    return {
        "effective HP": int(char.health / max(0.05, 1 - reduction)),
        "magic reduced": magic_cut,
        "phys reduced": char.get_physical_reduction_percent(),
        # REAL AVOIDANCE, NOT THE TALENT CONTRIBUTION. This read get_talent_effect("block") plus
        # get_talent_effect("dodge"), which is only the slice talents add - so it reported 0 dodge
        # for Primalist Mountain King, which actually has 24%, and it summed a block CHANCE with a
        # dodge chance from two different sources as though they were one number. Character.dodge
        # already includes the 5% baseline, agility at a quarter point each, talents and gear
        # suffixes; block and parry are likewise live percentages checked against one roll in
        # take_damage. Read them off the character.
        "dodge %": char.dodge,
        "parry %": getattr(char, "parry", 0.0),
        "block %": getattr(char, "block_chance", 0.0),
        "block value": getattr(char, "block_value", 0.0),
        "threat +%": char.get_talent_effect("threat_generation_pct") * 100,
        "net dmg/turn": dpt,
        "turns alive": (char.health / dpt) if dpt else 0,
    }


def healer_axes(char, level, gen, dress, fights):
    """What a healer is for: throughput, efficiency, and a big one when it matters.

    THE HEALER HEALS SOMEBODY ELSE. Three earlier versions had it healing itself while a creature
    hit it, and each produced a materially different picture - Restoration Druid read 60, then 71,
    then 69 healing a turn while Priest Holy read 314, and Grovekeeper swung between 51 and 4. The
    instrument was the problem, not the specs: self-healing while taking damage entangles three
    things at once (healing, incoming damage, and the clipping needed to keep a wound open), and
    heal-over-time specs are exactly the ones that entanglement eats.

    So the subject is a separate tank that soaks the damage, and the healer is never attacked. Every
    point of health the tank gains is healing, whenever it lands, with nothing else moving its bar
    upward. The healer stands there and heals, which is the job.
    """
    from combat.combat_engine import CombatEngine
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party

    learned = char.get_learned_abilities()
    heals = [a for a in learned
             if getattr(a, "effect_type", "") in ("heal", "hot", "damage_and_heal")]
    if not heals:
        # Keys must match the populated return exactly - `axes` is built from
        # whichever row comes back first, so a short dict here silently drops
        # an axis from the whole table.
        return {"healing/turn": 0, "healing/cast": 0, "healing/100 res": 0,
                "biggest heal": 0, "turns of mana": 0, "heal abilities": 0}

    patient = Character("Patient", "Warrior", level)
    dress(patient, gen, level)
    party = Party(char)
    party.add_member(patient)
    enemy = Monster("sparring", "beast_basic", level)
    engine = CombatEngine(char, enemy, party=party, enemies=[enemy])
    precast_stances(char, engine)
    enemy.current_health = 10 ** 6

    heals.sort(key=lambda a: -(getattr(a, "heal_value", 0) or 0))
    patient.current_health = max(1, patient.health // 2)
    healed, spent_mana, biggest, casts = 0, 0, 0, 0
    turns, dry_turn = 0, None
    previous = patient.current_health

    for _ in range(MAX_TICKS):
        engine.update(TICK)
        if not engine.is_active:
            break
        gain = patient.current_health - previous
        if gain > 0:
            healed += gain
            biggest = max(biggest, gain)
        # Hold the patient at half so no heal is ever wasted on a full bar and nothing dies. This
        # happens AFTER the gain is counted, which is what the earlier versions got wrong.
        patient.current_health = max(1, patient.health // 2)
        previous = patient.current_health

        actor = engine.current_actor
        if actor is None:
            continue
        if actor is not char:
            engine.execute_monster_action() if actor is enemy else engine.execute_defend(actor)
            continue
        turns += 1
        before_res = _resource_snapshot(char)
        cast_this_turn = False
        held_for_rolling = False
        for ability in heals:
            # DO NOT RE-CAST A HOT THAT IS STILL ROLLING. status_effects.py
            # line 30: "Re-applying an effect with the same effect_id
            # REFRESHES it (duration resets)". The priority loop below casts
            # the single highest-value castable heal EVERY turn at the same
            # patient, so before this guard every HoT was re-applied one turn
            # after it landed and threw away every remaining tick. Each cast
            # was therefore credited with roughly ONE tick, and since a tick
            # is effect_value/duration, the metric understated every
            # heal-over-time spec by a factor of its duration and rewarded
            # direct heals for free. That is why extending Rejuvenation from 4
            # turns to 6 - which is strictly more healing per cast - made the
            # numbers go DOWN, and why druid_restoration read 94 healing a
            # turn while its three HoTs summed to 254. A player lets a HoT
            # tick and spends the turn on the next target or a direct heal,
            # which is what skipping does here.
            if getattr(ability, "effect_type", "") == "hot" and \
                    patient.has_status_effect(ability.ability_id):
                held_for_rolling = True
                continue
            # AIM EACH HEAL WHERE IT ACTUALLY WORKS. damage_and_heal is cast
            # at an ENEMY and heals allies off the damage dealt - it is the
            # whole mechanic of Cultist Heretic ("Discipline-style
            # damage-that-heals loop - Malevolence and Gaze of C'Thun hit an
            # enemy while healing allies") and of Sun Cleric and Venomancer
            # Rot besides. Casting it at the patient simply FAILS, and a
            # failed cast spends nothing, which is why Heretic read 7
            # healing a turn, 0 healing per 100 mana, and 30 turns of mana
            # it never actually used: almost every cast was rejected and I
            # was reading the rejections as weak healing.
            aim = enemy if getattr(ability, "effect_type", "") == "damage_and_heal" else patient
            ok, _why = engine.execute_ability(char, ability.ability_id, aim)
            if ok:
                spent_mana += _resource_spend(before_res, _resource_snapshot(char))
                casts += 1
                cast_this_turn = True
                break
        # A TURN THE HEALER COULD NOT SPEND IS STILL A TURN. The window is
        # fixed (TURN_BUDGET) and runs to the end for every spec, so the
        # denominator of healing/turn is identical across the table and the
        # figures are directly comparable. Breaking out early - which this did
        # when it ran dry - divided a short window's healing by a short
        # denominator and flattered exactly the specs that could not sustain.
        if not cast_this_turn and not held_for_rolling and dry_turn is None:
            dry_turn = turns                                   # first turn it could not afford one
        gain = patient.current_health - previous
        if gain > 0:
            healed += gain
            biggest = max(biggest, gain)
        previous = patient.current_health
        if turns >= TURN_BUDGET:
            break

    return {
        # PER TURN, not per cast. This read `healed / casts` until 29 Oct,
        # which is healing per CAST under a "healing/turn" label. The two are
        # the same number only for a spec that casts every turn, i.e. a direct
        # healer; a HoT spec deliberately does not, so the old figure both
        # mislabelled the axis and double-punished heal-over-time kits on top
        # of the refresh bug fixed in the loop above. Throughput is what a
        # healer is judged on and throughput is per turn.
        "healing/turn": healed / turns if turns else 0,
        "healing/cast": healed / casts if casts else 0,
        # Named per 100 RESOURCE, not per 100 mana - see RESOURCE_POOLS.
        #
        # Floored at 1 rather than special-cased to 0, because zero spend
        # means INFINITE efficiency and reporting it as 0 ranked the best
        # spec on this axis as the worst. Cultist Heretic really does spend
        # nothing: its Sanity mechanic refunds 20-45 mana on every heal cast,
        # which is as much as the heal costs, so net spend is zero or
        # positive. Ritual of Awakening heals 2232 for a net 8 mana. A huge
        # number here is the honest answer and the spread it triggers is a
        # real finding, not an artefact.
        "healing/100 res": healed / max(1, spent_mana) * 100,
        "biggest heal": biggest,
        # Now literally what the label says: the turn on which the spec first
        # could not afford a heal, or the whole window if it never ran dry.
        # This used to be `casts`, which is a count of heals landed, not turns
        # of mana - a cheap-spell spec and an expensive-spell spec that both
        # emptied the pool scored the same.
        "turns of mana": dry_turn if dry_turn is not None else turns,
        "heal abilities": len(heals),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default="tank",
                    choices=sorted({r for s in SPEC_ROLES for r in roles_of(s)}))
    ap.add_argument("--level", type=int, default=60)
    ap.add_argument("--fights", type=int, default=8)
    args = ap.parse_args()

    import importlib.util
    spec_mod = importlib.util.spec_from_file_location("scb", ROOT / "tools/sim_class_balance.py")
    scb = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(scb)
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()

    specs = sorted(s for s in SPEC_ROLES if args.role in roles_of(s))
    measure = {"tank": tank_axes, "healer": healer_axes}.get(args.role)
    if measure is None:
        print(f"{args.role} is measured by tools/sim_class_balance.py - kill speed is the right "
              f"question for a damage spec and the wrong one for the other roles.")
        return 0

    print(f"{len(specs)} {args.role} specs at level {args.level}, talents spent\n")
    rows = {}
    for spec in specs:
        char, spent = build(spec, args.level, gen, scb.dress, role=args.role)
        rows[spec] = measure(char, args.level, gen, scb.dress, args.fights)
        rows[spec]["_points"] = spent

    axes = [k for k in next(iter(rows.values())) if not k.startswith("_")]
    # NOT EVERY AXIS IS BETTER WHEN IT IS BIGGER. Ranking all of them descending reported
    # venomancer_fortitude - which took the MOST damage per turn of any tank, 235 against the
    # Protection Warrior's 131 - as the best tank at not taking damage, and gave the Warrior no
    # credit for the axis it actually wins. Anything measuring a cost is ranked the other way.
    LOWER_IS_BETTER = {"net dmg/turn"}
    width = max(len(s) for s in specs) + 2
    print("  " + "spec".ljust(width) + "".join(f"{a:>18}" for a in axes))
    for spec in specs:
        line = "  " + spec.ljust(width)
        for a in axes:
            line += f"{rows[spec][a]:>18.0f}"
        print(line)

    # ---- the three failures worth naming. Everything else is the design working.
    print("\nFINDINGS (balanced does not mean identical - only these three shapes are problems)")
    ranks = {a: sorted(specs, key=lambda s: (rows[s][a] if a in LOWER_IS_BETTER
                                             else -rows[s][a])) for a in axes}
    problems = []
    for spec in specs:
        places = [ranks[a].index(spec) for a in axes]
        if all(p == len(specs) - 1 for p in places):
            problems.append(f"{spec} is LAST on every axis - no compensating strength")
        if all(p == 0 for p in places):
            problems.append(f"{spec} is FIRST on every axis - leaves its peers no reason to exist")
        best = [a for a in axes if ranks[a][0] == spec]
        if not best:
            worst_half = [a for a in axes if places[axes.index(a)] >= len(specs) / 2]
            if len(worst_half) == len(axes):
                problems.append(f"{spec} is in the bottom half of every axis and best at nothing")
    for a in axes:
        vals = [rows[s][a] for s in specs if rows[s][a] > 0]
        if len(vals) > 2 and min(vals) and max(vals) / min(vals) > 4:
            problems.append(f"{a}: {max(vals)/min(vals):.1f}x spread between "
                            f"{ranks[a][0]} and {ranks[a][-1]}")
        zero = [s for s in specs if rows[s][a] == 0 and a not in LOWER_IS_BETTER]
        if zero and len(zero) < len(specs):
            problems.append(f"{a}: {', '.join(zero)} score zero where every peer scores something")
    if problems:
        for p in dict.fromkeys(problems):
            print(f"  - {p}")
    else:
        print("  none - every spec is viable and each is best at something")

    print("\n  each spec's best axis:")
    for spec in specs:
        best = [a for a in axes if ranks[a][0] == spec]
        print(f"    {spec:<{width}}{', '.join(best) if best else 'nothing'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
