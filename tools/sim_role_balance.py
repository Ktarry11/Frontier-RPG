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
    "primalist_grovekeeper": "healer", "tinker_invention": "healer",
    "venomancer_vizier": "healer", "cultist_heretic": "healer", "stormbringer_wind": "healer",
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


#: What a tank is hit by while being measured: the hardest thing in the game at its own level.
TANK_ATTACKER = "elemental_caster"
TANK_PHYSICAL = "beast_large"

TICK = 0.05
MAX_TICKS = 20000


def roles_of(spec):
    r = SPEC_ROLES[spec]
    return (r,) if isinstance(r, str) else tuple(r)


def class_of(spec):
    """'sun_cleric_seraphim' -> 'Sun Cleric'. Longest matching class slug wins, so multi-word
    class names are not split at the wrong underscore."""
    slugs = sorted((p.stem for p in (ROOT / "data/abilities").glob("*.json")),
                   key=len, reverse=True)
    for slug in slugs:
        if spec.startswith(slug + "_"):
            return slug.replace("_", " ").title()
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
        keys = " ".join((node.effects or {})).lower() + " " + (node.name or "").lower()
        return any(w in keys for w in wanted)

    # Tiers gate on points already spent, so this walks up from the bottom - which is also how a
    # player is forced to spend them - taking role-relevant nodes first on each tier.
    for tier in range(0, tree.get_max_tier() + 1):
        ordered = sorted(tree.get_nodes_in_tier(tier), key=lambda n: not relevant(n))
        for node in ordered:
            while spent < budget:
                ok = node.can_spend_point(tree) if takes_tree else node.can_spend_point()
                if not ok or not node.spend_point():
                    break
                spent += 1
    for sync in ("_sync_talent_procs", "_sync_talent_unlocked_abilities",
                 "_recalculate_derived_stats", "_refresh_ability_ranks"):
        if hasattr(char, sync):
            try:
                getattr(char, sync)()
            except Exception:                                   # noqa: BLE001
                pass
    dress(char, gen, level)
    for form in ROLE_FORMS.get(role or "", []):
        if hasattr(char, "can_use_form") and char.can_use_form(form):
            char.shift_form(form)
            break
    return char, spent


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

    taken = []
    for template in (TANK_ATTACKER, TANK_PHYSICAL):
        for _ in range(max(1, fights // 2)):
            char.current_health = char.health
            enemy = Monster("hitter", template, level)
            engine = CombatEngine(char, enemy, party=Party(char))
            enemy.current_health = 10 ** 6          # measure survival, not the tank's damage
            turns, samples = 0, []
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
                    for ability in rotation:
                        if engine.execute_ability(char, ability.ability_id, enemy)[0]:
                            acted = True
                            break
                    if not acted:
                        engine.execute_defend(char)
                    continue
                before = char.current_health
                engine.execute_monster_action()
                hit = before - char.current_health
                if hit > 0:
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
        "block+dodge": char.get_talent_effect("block") + char.get_talent_effect("dodge"),
        "threat +%": char.get_talent_effect("threat_generation_pct") * 100,
        "dmg taken/turn": dpt,
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
        return {"healing/turn": 0, "healing/100 mana": 0, "biggest heal": 0,
                "turns of mana": 0, "heal abilities": 0}

    patient = Character("Patient", "Warrior", level)
    dress(patient, gen, level)
    party = Party(char)
    party.add_member(patient)
    enemy = Monster("sparring", "beast_basic", level)
    engine = CombatEngine(char, enemy, party=party, enemies=[enemy])
    enemy.current_health = 10 ** 6

    heals.sort(key=lambda a: -(getattr(a, "heal_value", 0) or 0))
    patient.current_health = max(1, patient.health // 2)
    healed, spent_mana, biggest, casts = 0, 0, 0, 0
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
        before_mana = getattr(char, "current_mana", 0)
        for ability in heals:
            ok, _why = engine.execute_ability(char, ability.ability_id, patient)
            if ok:
                spent_mana += max(0, before_mana - getattr(char, "current_mana", 0))
                casts += 1
                break
        else:
            break                                              # nothing castable: out of resources
        gain = patient.current_health - previous
        if gain > 0:
            healed += gain
            biggest = max(biggest, gain)
        previous = patient.current_health
        if casts >= 30:
            break

    return {
        "healing/turn": healed / casts if casts else 0,
        "healing/100 mana": (healed / spent_mana * 100) if spent_mana else 0,
        "biggest heal": biggest,
        "turns of mana": casts,
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
    LOWER_IS_BETTER = {"dmg taken/turn"}
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
