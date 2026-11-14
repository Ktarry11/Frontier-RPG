#!/usr/bin/env python3
"""How many turns to kill a mob, and how many turns for it to kill you?

    PYTHONPATH=. python3 tools/audit_time_to_kill.py [--levels 10,26,40,60]

Kyle, 7 Nov, with a combat log on screen:

    "a lvl 26 critting for almost 600 vs a mob that has 400 hp? lmao"

    Adrian Mendoza uses Righteous Lunge for 581 damage! (CRIT!)
    Ambermill Ghost-Mage uses Arcane Missiles on Venom for 26 damage!
    Tarek Mansour uses Attack for 147 damage!

Two numbers decide whether a fight is a fight, and neither of them is damage
on its own - damage only means something against the health it is being
spent on. So this measures the pair:

    PLAYER TTK   turns for one party member to kill one level-appropriate
                 mob, using its real rotation through real Ability objects.
    MOB TTK      turns for that mob to kill that party member.

A fight is interesting when MOB TTK is comfortably larger than PLAYER TTK but
not enormously so. When PLAYER TTK is 1 the mob never takes a turn, and
nothing about its kit, its resistances or its row matters - which is the state
Kyle is describing, and the reason a whole session of row and resistance work
can be invisible in play.

IT MEASURES, IT DOES NOT FIX. The output names which half is wrong - player
damage too high, mob health too low, or mob damage too low - because those are
three different edits in three different files and guessing between them is
how the last four balance bugs in this repo got made.
"""

import argparse
import collections
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_LEVELS = (10, 26, 40, 60)

#: One per archetype. Same list the avoidance audit uses, so the two reports
#: describe the same characters.
SUBJECTS = [("Warrior", True), ("Paladin", True), ("Rogue", False),
            ("Hunter", False), ("Mage", False)]

#: A fight that has not resolved by here is reported as ">N" rather than left
#: to run - an unkillable pair is itself the finding.
TURN_CAP = 40


def _build(char_class, level, rarity="uncommon", shield=False):
    from entities.character import Character
    from entities.loot_generator import LootGenerator
    actor = Character(name="Subject", char_class=char_class, level=level)
    gen = LootGenerator()
    for slot in list(actor.equipment.slots or {}):
        try:
            item = gen.generate_item_for_class(actor.char_class, actor.level,
                                               slot=slot, rarity=rarity)
        except Exception:
            continue
        if item is None:
            continue
        actor.inventory.append(item)
        if not actor.equip_item(item):
            actor.inventory.remove(item)
    if shield:
        try:
            sh = gen.generate_item_for_class(actor.char_class, actor.level,
                                             slot="off_hand", rarity=rarity,
                                             weapon_type="shield")
            actor.inventory.append(sh)
            if not actor.equip_item(sh):
                actor.inventory.remove(sh)
        except Exception:
            pass
    return actor


def _creatures_at(level, span=2):
    """Real creatures whose level band contains `level`."""
    with open(os.path.join(ROOT, "data/creatures/creatures.json"), encoding="utf-8") as fh:
        doc = json.load(fh)
    # creatures.json is a NAME -> record map, not a list. Iterating it
    # directly yields names, which is how the first run of this tool asked a
    # string for .get("level_range").
    creatures = doc.get("creatures", doc)
    out = []
    for name, c in creatures.items():
        if not isinstance(c, dict):
            continue
        lr = c.get("level_range") or []
        if len(lr) == 2 and lr[0] is not None and lr[0] - span <= level <= lr[1] + span:
            if c.get("is_boss") or c.get("elite"):
                continue
            rec = dict(c)
            rec.setdefault("name", name)
            out.append(rec)
    return out


def _damage_abilities(actor):
    """Castable damaging abilities, biggest first once measured.

    Read off ability_book, which is the same place execute_ability looks -
    reconstructing a damage formula here would make this tool a SECOND source
    of truth about damage, and the whole point of it is to check the first.
    """
    book = getattr(actor, "ability_book", None)
    if book is None:
        return []
    try:
        abilities = list(book.get_all_abilities())
    except Exception:
        try:
            abilities = list(book.abilities.values())
        except Exception:
            return []
    out = []
    for a in abilities:
        et = getattr(a, "effect_type", "")
        if et in ("damage", "ranged_damage", "spell_damage", "damage_and_heal"):
            out.append(a)
    return out


def _real_hit(actor, mob, ability):
    """Cast it in a real CombatEngine and read the health that came off.

    No crit, no miss: the engine is asked for a hit and the result measured,
    then the mob is restored. The spread is reported separately as the crit
    multiple, because an average hides exactly the case Kyle screenshotted.
    """
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    party = Party(actor)
    engine = CombatEngine(actor, mob, party=party, enemies=[mob])
    before = mob.current_health
    try:
        engine.execute_ability(actor, ability.ability_id, mob)
    except Exception:
        return 0.0
    dealt = before - mob.current_health
    mob.current_health = before
    return max(0.0, float(dealt))


def _real_mob_hit(actor, mob, samples=6):
    """Median damage the mob actually lands, through execute_monster_action.

    MEASURED, not derived. The first version of this tool computed it as
    attack_power/14*2 + damage, which is a reconstruction of a formula that
    lives somewhere else - the exact mistake this file's docstring complains
    about. It also disagreed with the combat log Kyle screenshotted (it said
    11, the log said 26-55), and when a tool and the game disagree the tool
    is wrong until proven otherwise.
    """
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    dealt = []
    for _ in range(samples):
        party = Party(actor)
        engine = CombatEngine(actor, mob, party=party, enemies=[mob])
        before = actor.current_health
        try:
            engine.current_actor = mob
            engine.execute_monster_action()
        except Exception:
            actor.current_health = before
            continue
        hit = before - actor.current_health
        actor.current_health = before
        if hit > 0:
            dealt.append(float(hit))
    return statistics.median(dealt) if dealt else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default=",".join(str(x) for x in DEFAULT_LEVELS))
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",") if x.strip()]

    from entities.monster import Monster

    print(f"  one party member against one same-level non-elite mob\n")
    print(f"  {'lvl':>4}{'class':10}{'player hp':>10}{'mob hp':>8}"
          f"{'best hit':>10}{'auto':>7}{'mob hit':>9}"
          f"{'kill in':>9}{'dies in':>9}")

    verdicts = []
    for level in levels:
        pool = _creatures_at(level)
        if not pool:
            print(f"  {level:>4}  no creatures in band")
            continue
        for char_class, shield in SUBJECTS:
            actor = _build(char_class, level, shield=shield)
            dmg_pool = _damage_abilities(actor)
            hps, mobhits, bests, autos, ttk_p, ttk_m = [], [], [], [], [], []
            for c in pool[:30]:
                try:
                    # Monster(name, monster_type, level, kit) - it does NOT
                    # take the creatures.json record, it takes the template
                    # key out of it. Passing the dict raised, and the bare
                    # except around it turned every creature into a silent
                    # skip and printed an empty report.
                    mob = Monster(c["name"], c["template"], level=level,
                                  kit=c.get("ability_kit"))
                except Exception as exc:
                    if not hasattr(main, "_warned"):
                        print(f"  (skipping creatures: {exc})")
                        main._warned = True
                    continue
                mhp = getattr(mob, "max_health", 0) or 0
                if not mhp:
                    continue
                best = 0.0
                for ability in dmg_pool:
                    # Several samples: an ability rolls a range, and one
                    # sample of a wide range is not a number worth printing.
                    rolls = [_real_hit(actor, mob, ability) for _ in range(5)]
                    best = max(best, max(rolls) if rolls else 0.0)
                auto = best
                hit = max(best, 1.0)
                mob_dmg = _real_mob_hit(actor, mob)
                hps.append(mhp)
                bests.append(best)
                autos.append(auto)
                if mob_dmg <= 0:
                    continue
                mobhits.append(mob_dmg)
                ttk_p.append(max(1, round(mhp / max(1.0, hit))))
                ttk_m.append(max(1, round(getattr(actor, "max_health", None) or actor.health / max(1.0, mob_dmg))))
            if not hps:
                continue
            med = statistics.median
            pk, dk = med(ttk_p), med(ttk_m)
            verdicts.append((level, char_class, pk, dk))
            print(f"  {level:>4}{char_class:10}{getattr(actor, "max_health", None) or actor.health:>10}"
                  f"{med(hps):>8.0f}{med(bests):>10.0f}{med(autos):>7.0f}"
                  f"{med(mobhits):>9.0f}{pk:>9.0f}{dk:>9.0f}")

    print("\n  -- verdict -------------------------------------------------")
    one_shot = [(l, c) for l, c, pk, _d in verdicts if pk <= 1]
    fast = [(l, c) for l, c, pk, _d in verdicts if pk <= 2]
    if one_shot:
        print(f"  {len(one_shot)} of {len(verdicts)} cases kill a same-level mob "
              f"in ONE turn - the mob never acts:")
        for l, c in one_shot[:10]:
            print(f"       lvl {l:<3} {c}")
    print(f"  {len(fast)} of {len(verdicts)} kill in two turns or fewer")
    ratios = [d / max(1, p) for _l, _c, p, d in verdicts]
    if ratios:
        print(f"  median (turns to die) / (turns to kill) = "
              f"{statistics.median(ratios):.1f}x")
        print("  under ~3x the mob is a speed bump; over ~12x the player is "
              "never in danger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
