#!/usr/bin/env python3
"""Catch talent interactions that only break once a whole tree is maxed.

    python3 tools/check_talent_balance.py            # every class
    python3 tools/check_talent_balance.py paladin    # one class

Written after the Paladin Protection redesign, where reading the fully-maxed
tree back produced three bugs that were invisible in the per-talent data:

  low_health_threshold_pct SUMMED. Ardent Defender and Divine Guardian each
    set 0.35 and the character ended up at 0.70 - "below 70% health" instead
    of 35%. A threshold is not a quantity; exactly one talent may define it.
  Avenger's Shield's cooldown reached ZERO - 1 per rank over 3 ranks against
    a 3-turn cooldown.
  Divine Shield went 6 -> 2 turns because two separate talents both reduced
    it.

None of those are visible in a single talent. They only exist in the sum, so
the check has to build a real character, max every node, and look at what the
engine actually ends up with - which is what this does.
"""
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Keys that describe a THRESHOLD or a STATE, not an amount. Summing them is
#: always a bug: two talents each saying "below 35% health" must not produce
#: "below 70% health".
THRESHOLD_KEYS = {
    "low_health_threshold_pct",
}

#: Percentage-style keys that should never reach these magnitudes from
#: talents alone. Generous on purpose - this is for catching a tree that
#: accidentally grants 100% dodge, not for tuning.
#: Caps are expressed in each key's OWN unit, which is not the same for all
#: of them. The ten keys the engine divides by 100 (armor_pct, stamina_pct,
#: healing_power_pct, ...) take percentage POINTS, so their caps are points;
#: every other _pct key is a fraction, so its cap is a fraction. Treating
#: armor_pct as a fraction here reported a perfectly reasonable +6% Armor as
#: a tenfold cap breach - the checker has to know the convention split just
#: as the audit does.
SANITY_CAPS = {
    # fraction-unit keys
    "damage_taken_pct": 0.50, "magic_damage_taken_pct": 0.50,
    "physical_damage_taken_pct": 0.50,
    "max_health_pct": 0.60, "max_mana_pct": 0.60,
    "low_health_damage_reduction_pct": 0.60,
    "stun_duration_reduction_pct": 1.0,
    "threat_generation_pct": 3.0,
    # points-unit keys (value 20 == +20%)
    "armor_pct": 60.0, "stamina_pct": 40.0, "healing_power_pct": 50.0,
    "attack_power_pct": 50.0, "agility_pct": 40.0, "intellect_pct": 40.0,
    "spirit_pct": 40.0, "strength_pct": 40.0, "all_stats_pct": 30.0,
    # plain stats
    "dodge": 40.0, "parry": 40.0, "block": 80.0,
    "crit_chance_physical": 60.0, "crit_chance_spell": 60.0,
}

#: Every playable class, classic AND Frontier homebrew. The homebrew ones
#: were missing for a long time, which meant none of these checks ever ran
#: against roughly half the talents in the game - and that is where the data
#: is weakest. It immediately found a Venomancer talent modifying
#: 'venomancer_lifeblood', an ability that does not exist.
CLASSES = ["Warrior", "Paladin", "Hunter", "Rogue", "Priest",
           "Shaman", "Mage", "Warlock", "Druid",
           "Cultist", "Runemaster", "Starcaller", "Sun Cleric",
           "Tinker", "Venomancer", "Stormbringer", "Primalist"]


def main():
    only = sys.argv[1].lower() if len(sys.argv) > 1 else None
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    from entities.character import Character

    failures = []
    checked = 0

    for cls in CLASSES:
        if only and cls.lower() != only:
            continue
        c = Character("Check", cls, 60)
        if not getattr(c, "talent_trees", None):
            continue
        checked += 1

        # Max every node in every tree this class has.
        contributors = defaultdict(list)
        for tname, tree in c.talent_trees.items():
            for node in tree.nodes.values():
                node.points_spent = node.max_points
                for k, v in (node.effects or {}).items():
                    if isinstance(v, (int, float)):
                        contributors[k].append((tname, node.name, v * node.max_points))

        totals = c.get_talent_effects()

        # 1. threshold keys must have exactly one contributor
        for key in THRESHOLD_KEYS:
            src = contributors.get(key, [])
            if len(src) > 1:
                failures.append(
                    f"{cls}: {key} set by {len(src)} talents and SUMS to "
                    f"{round(totals.get(key, 0), 3)} - "
                    + ", ".join(f"{n} ({t})" for t, n, _ in src))

        # 2. sanity caps
        for key, cap in SANITY_CAPS.items():
            val = totals.get(key)
            if isinstance(val, (int, float)) and abs(val) > cap:
                src = contributors.get(key, [])
                failures.append(
                    f"{cls}: {key} reaches {round(val, 3)} (cap {cap}) from "
                    + ", ".join(f"{n}" for _, n, _ in src))

        # Every ability_id this class can actually cast. Checks 5 and 6 both
        # compare authored ids against it.
        known = {a.ability_id for a in c.ability_book.get_all_abilities()}

        # 3. cooldown reductions must not overshoot the base.
        #
        # Ability.talented_cooldown floors at 1 turn for anything that has a
        # cooldown, so an overshoot no longer produces a spammable ability -
        # but it does mean ranks the player paid for buy nothing, and the
        # tooltip promises a reduction that never lands. Flag the authoring,
        # not the symptom.
        for ab in c.ability_book.get_all_abilities():
            base = getattr(ab, "cooldown", 0) or 0
            if base <= 0:
                continue
            key = f"ability_{ab.ability_id}_cooldown"
            total = totals.get(key, 0)
            if total >= base:
                src = contributors.get(key, [])
                failures.append(
                    f"{cls}: {ab.name} cooldown base {base} but talents reduce it by "
                    f"{round(total, 2)} - ranks past {base - 1} are wasted ("
                    + ", ".join(f"{n}" for _, n, _ in src) + ")")

        # 3b. resource-cost reductions must not overshoot the base either.
        #
        # Costs floor at 0, so a reduction larger than the cost both wastes
        # ranks and makes the ability free, removing the resource tension it
        # was designed around. Caught Tactical Mastery taking Overpower (5
        # Rage) and Execute (15) to zero with -10.
        for ab in c.ability_book.get_all_abilities():
            base = int(getattr(ab, "cost", 0) or 0)
            if base <= 0:
                continue
            key = f"ability_{ab.ability_id}_cost"
            total = totals.get(key, 0)
            if total >= base:
                src = contributors.get(key, [])
                failures.append(
                    f"{cls}: {ab.name} costs {base} but talents reduce it by "
                    f"{round(total, 2)} - it becomes free and the excess is wasted ("
                    + ", ".join(f"{n}" for _, n, _ in src) + ")")

        # 4. a proc's chance must be a real chance at one rank.
        #
        # The engine clamps rank-scaled chance with min(100, ...) in
        # Character._sync_talent_procs, so a 100%-at-rank-1 proc on a
        # multi-rank node is fine and intentional (the ranks scale the
        # node's `effects`, not the proc). Only a single rank already
        # over 100 is an authoring error.
        for tname, tree in c.talent_trees.items():
            for node in tree.nodes.values():
                proc = getattr(node, "proc", None)
                if not proc or "chance" not in proc:
                    continue
                if proc["chance"] > 100:
                    failures.append(
                        f"{cls}: {node.name} proc chance is {proc['chance']}% at one rank")
                # A multi-rank node whose proc is already at 100% gets nothing
                # from its extra ranks unless its `effects` scale too - the
                # player pays for ranks that cannot do anything.
                if (proc["chance"] >= 100 and node.max_points > 1
                        and not node.effects):
                    failures.append(
                        f"{cls}: {node.name} is {node.max_points} ranks but its proc is "
                        f"already 100% at rank 1 and it has no scaling effects - "
                        f"ranks 2+ buy nothing")

        # 6. a proc's ability_filter must name abilities the class can cast.
        #    A typo here does not error: the filter simply never matches and
        #    the proc silently never fires.
        for tname, tree in c.talent_trees.items():
            for node in tree.nodes.values():
                proc = getattr(node, "proc", None) or {}
                filt = proc.get("ability_filter") or []
                if isinstance(filt, str):
                    filt = [filt]
                for aid in filt:
                    if aid not in known:
                        failures.append(
                            f"{cls}: {node.name} proc filters on '{aid}', which this "
                            f"class has no ability for - the proc can never fire")

        # 7. unlock_ability talents and the requires_talent flag must agree.
        #
        # The gate itself works: an ability carrying requires_talent=True is
        # not learned until some talent unlocks it (verified at runtime - a
        # pristine level-60 Rogue cannot cast Mutilate, Shadow Dance or
        # Preparation). What can go wrong is the two sides disagreeing, in
        # either direction, and both are silent.
        #
        # NOTE for anyone extending this: ability_book.get_all_abilities()
        # returns every ability INCLUDING unlearned ones, so it cannot be
        # used to ask "does this character know X". An earlier version of
        # this check did exactly that and reported all 74 unlock talents in
        # the game as no-ops. They are fine. Compare against requires_talent.
        by_id = {a.ability_id: a for a in c.ability_book.get_all_abilities()}
        unlocked_by_talent = set()
        for tname, tree in c.talent_trees.items():
            for node in tree.nodes.values():
                unlock = (node.effects or {}).get("unlock_ability")
                for aid in ([unlock] if isinstance(unlock, str) else (unlock or [])):
                    unlocked_by_talent.add(aid)
                    ab = by_id.get(aid)
                    if ab is None:
                        failures.append(
                            f"{cls}: {node.name} unlocks '{aid}', which is not an "
                            f"ability this class has at all")
                    elif not getattr(ab, "requires_talent", False):
                        failures.append(
                            f"{cls}: {node.name} unlocks '{ab.name}', but that ability "
                            f"is not flagged requires_talent - the class gets it for "
                            f"free and the talent point buys nothing")
        # the other direction: flagged as talent-gated, but nothing grants it
        for ab in by_id.values():
            if getattr(ab, "requires_talent", False) and ab.ability_id not in unlocked_by_talent:
                failures.append(
                    f"{cls}: {ab.name} is flagged requires_talent but no talent "
                    f"unlocks it - it is permanently unreachable")

        # 5. an ability modifier naming an ability this class cannot cast
        for key in totals:
            if not isinstance(key, str) or not key.startswith("ability_"):
                continue
            # Longest suffix first. "_crit_damage", "_cost_pct" and
            # "_cooldown_pct" all END with a shorter valid suffix, so a
            # shortest-first scan strips the wrong amount and invents an
            # ability id: ability_x_crit_damage was reported as targeting
            # "x_crit" rather than "x", a false positive on correct data.
            for suffix in ("_crit_damage", "_cooldown_pct", "_cost_pct",
                           "_healing", "_cooldown", "_duration", "_potency",
                           "_damage", "_crit", "_cost"):
                if key.endswith(suffix):
                    aid = key[len("ability_"):-len(suffix)]
                    if aid not in known:
                        failures.append(
                            f"{cls}: {key} targets '{aid}', which this class has no ability for")
                    break

    pygame.quit()
    print(f"checked {checked} classes with every talent maxed\n")
    if not failures:
        print("No balance problems found.")
        return 0
    print(f"{len(failures)} PROBLEMS\n" + "=" * 68)
    for f in failures:
        print(f"  {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
