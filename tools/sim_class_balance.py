#!/usr/bin/env python3
"""Fight every class at every level through the real combat engine and compare how they do.

    PYTHONPATH=. python3 tools/sim_class_balance.py [--fights 40] [--levels 5,10,...] [--class Rogue]

Kyle, 2026-10-28: "i want to ensure that all classes are balanced from 1-60."

THIS SIMULATES, IT DOES NOT COMPARE STAT TABLES. Reading damage coefficients off 655 abilities and
adding them up would produce a confident number that has never been tested against armour,
mitigation, resources, cooldowns, crit, the turn meter or the order things actually resolve in. The
engine is the only thing that knows what a class does; everything else is me guessing at it. So each
data point is real fights, run turn by turn through CombatEngine.

ONE POLICY FOR ALL SEVENTEEN CLASSES, or the measurement is of my rotations rather than of the
classes. The policy is deliberately simple and identical: heal when badly hurt and a heal is
available, otherwise use the hardest-hitting thing that works, otherwise swing. Crucially it does
not decide what "works" means - it tries abilities in order and lets execute_ability refuse, so
cooldowns, resource costs, form and weapon requirements are all enforced by the engine's own gates
rather than re-derived here. Re-deriving game rules in a verifier is how most of this session's
false findings happened.

GEAR MATTERS MORE THAN ANYTHING. An ungeared level-40 Warrior loses to a level-40 boar, so every
class is dressed from LootGenerator at its own level before the bell: every slot, class-appropriate,
and routed through equip_item so proficiency rules apply - a Priest really cannot wear the plate.

WHAT IT REPORTS, and what counts as a problem: win rate against a same-level creature, turns to
kill, and health left at the end. A class that cannot beat its own level is broken; one that wins in
half the turns of everybody else is a different kind of broken. Both show up as outliers against the
spread, which is the only honest bar when there is no external reference to measure against.
"""
import argparse
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Not real playable classes - a shared pool and one scripted companion.
NOT_A_CLASS = {"_universal", "asher_unique"}

#: Enemy templates a solo player meets in the open world, weighted by how ordinary they are.
#: A single template would measure each class against one damage profile, and classes differ a lot
#: in how they handle a caster versus a heavy hitter.
ENEMY_MIX = ["beast_basic", "beast_basic", "humanoid_warrior", "humanoid_caster", "beast_fast"]

#: Equipment slots to fill, in equip order. Two-handers displace the off-hand, which is fine.
GEAR_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back",
              "main_hand", "off_hand", "ranged"]

#: dt per engine tick. Small enough that the turn meter resolves one actor at a time.
TICK = 0.05

#: Hard stop so a stalemate (two combatants who cannot kill each other) ends the fight rather
#: than the process.
MAX_TICKS = 20000


def enemy_level(level, above):
    """A FIXED LEVEL GAP IS NOT A FIXED DIFFICULTY. "Ten levels above" is a doubling at level 10 and
    a sixth at level 60, which made the first sweep read 0% for every class at level 10 and told us
    nothing except that a level-20 creature kills a level-10 character. The gap is proportional."""
    return max(level + 2, int(round(level * (1.0 + above))))


def classes():
    names = sorted(p.stem for p in (ROOT / "data/abilities").glob("*.json")
                   if p.stem not in NOT_A_CLASS)
    # char_class is the display name ("Sun Cleric"), the files are slugs ("sun_cleric").
    return [(slug, slug.replace("_", " ").title()) for slug in names]


def dress(char, gen, level):
    """Equip a level-appropriate set. Returns how many pieces went on."""
    worn = 0
    for slot in GEAR_SLOTS:
        rarity = "uncommon" if level < 20 else "rare"
        try:
            item = gen.generate_item_for_class(char.char_class, level, slot=slot, rarity=rarity)
        except Exception:                                      # noqa: BLE001
            continue
        if item is None:
            continue
        # equip_item requires the item to be in inventory, and enforces proficiency there - a
        # Priest handed plate is refused, which is the behaviour we want represented.
        char.inventory.append(item)
        if char.equip_item(item):
            worn += 1
        elif item in char.inventory:
            char.inventory.remove(item)
    return worn


#: The real effect_type vocabulary, counted out of data/abilities rather than assumed. The first
#: version of this guessed "damage", "damage_over_time" and "damage_aoe" - two of which do not
#: exist - and so excluded spell_damage (79 abilities) and spell_dot (48) outright. Every caster was
#: then fighting with its basic attack only, and the sweep that produced said a level-40 Priest had
#: ONE offensive ability. It has eight. Nothing about that measurement was real.
OFFENSIVE = {"damage", "spell_damage", "spell_dot", "dot", "ranged_damage",
             "damage_and_heal", "damage_and_restore_mana"}
RESTORATIVE = {"heal", "hot", "damage_and_heal", "damage_and_restore_mana"}


def plan(char):
    """(heals, attacks) in preference order. Built once; the engine decides what is usable."""
    learned = char.get_learned_abilities()
    heals = [a for a in learned if getattr(a, "effect_type", "") in RESTORATIVE]
    attacks = [a for a in learned if getattr(a, "effect_type", "") in OFFENSIVE]
    heals.sort(key=lambda a: -(getattr(a, "heal_value", 0) or 0))
    attacks.sort(key=lambda a: -(getattr(a, "effect_value", 0) or 0))
    return heals, attacks


def fight(char, enemy_template, level, gen, rng):
    """Run one fight to a conclusion. Returns (won, turns, health_fraction_left)."""
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party

    char.current_health = char.health
    if getattr(char, "mana", 0):
        char.current_mana = char.mana
    enemy = Monster(f"{enemy_template} {level}", enemy_template, level)
    engine = CombatEngine(char, enemy, party=Party(char))

    heals, attacks = plan(char)
    turns = 0
    #: HEALING HAS TO BE RATIONED OR HEALERS HEAL-LOCK. With a bare "heal below 35%" rule, a class
    #: whose heal does not outpace incoming damage never climbs back over the threshold and so
    #: heals every remaining turn: the Shaman spent 17 of 28 turns casting Healing Wave and its
    #: win rate read 40%, which measured this loop rather than the class. A real player heals, gets
    #: back to work, and heals again when it is worth a turn. One heal every third turn at most.
    HEAL_EVERY = 3
    last_heal = -HEAL_EVERY
    for _ in range(MAX_TICKS):
        engine.update(TICK)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is not char:
            engine.execute_monster_action()
            continue

        turns += 1
        acted = False
        hurt = char.health and char.current_health / char.health < 0.35
        may_heal = hurt and heals and (turns - last_heal) >= HEAL_EVERY
        order = (heals + attacks) if may_heal else attacks
        # DON'T REAPPLY A DOT THAT IS STILL TICKING. Sorting by total effect value puts damage-over-
        # time first, since its total is the sum of its ticks, so a naive loop re-casts Rend or
        # Shadow Word: Pain every single turn and overwrites it. Some carry a cooldown and the engine
        # refuses, but not all of them do, and the ones that don't would have their class measured
        # as though its whole rotation were one spell cast repeatedly.
        live = {getattr(fx, "effect_id", None) for fx in getattr(enemy, "active_effects", [])}
        for ability in order:
            if ability.ability_id in live:
                continue
            ok, _why = engine.execute_ability(char, ability.ability_id, enemy)
            if ok:
                acted = True
                if ability in heals:
                    last_heal = turns
                break
        if not acted:
            engine.execute_defend(char)

    won = bool(getattr(engine, "victory", False))
    left = (char.current_health / char.health) if char.health else 0.0
    return won, turns, max(0.0, left)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=20)
    ap.add_argument("--levels", default="5,10,20,30,40,50,60")
    ap.add_argument("--class", dest="only", default=None)
    # WHY THE BENCHMARK IS ONLY SLIGHTLY ABOVE THE PLAYER'S LEVEL.
    #
    # This defaulted to 0.25 on the reasoning that a same-level fight reads
    # 100% for everyone and separates nothing, so a big gap is needed to
    # make outcomes diverge. That reasoning holds at low level and breaks
    # badly at high level, because the gap is a PERCENTAGE: +2 levels at 5,
    # but +15 at 60. At +15 the test stops measuring damage and starts
    # measuring whether your armour class survives three hits, which cloth
    # never will. The level 60 table read:
    #
    #   physical   Hunter 83, Rogue 75, Cultist 58, Guardian 58, Warrior 50
    #   casters    Mage, Priest, Warlock, Shaman, Runemaster, Starcaller,
    #              Stormbringer, Sun Cleric, Paladin, Druid ALL 0%
    #
    # which reads as every caster in the game being broken. They are not:
    # traced directly, a level 60 Priest casts its whole kit successfully
    # (Smite 98, Shadow Word: Pain 99 over 4 turns, Holy Fire 96) and
    # nobody runs out of mana. It has 708 health in cloth and a level 75
    # creature kills it in three swings. The benchmark was the finding.
    #
    # At a fair gap win rate saturates, exactly as the old comment said -
    # and that is fine, because TURNS TO KILL is then the discriminator and
    # it separates cleanly: 2.1 for a Rogue to 5.2 for a Paladin at 60.
    # Win rate at a fair gap is a floor check ("can this class function"),
    # kill speed is the comparison. Pass --above 0.25 deliberately to ask
    # the different question of who survives an overwhelming pull.
    ap.add_argument("--above", type=float, default=0.05,
                    help="enemy level = character level x (1 + this), min +2 (default 0.05)")
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",")]

    from entities.character import Character
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    rng = random.Random(0)

    roster = [(s, d) for s, d in classes() if not args.only or d.lower() == args.only.lower()]
    if not roster:
        print(f"no class matching {args.only!r}. known: "
              + ", ".join(d for _s, d in classes()))
        return 1

    print(f"{len(roster)} classes x {len(levels)} levels x {args.fights} fights against "
          f"{len(set(ENEMY_MIX))} enemy templates, each at level x{1+args.above:.2f}\n"
          f"  enemy level by player level: " +
          ", ".join(f"{lv}->{enemy_level(lv, args.above)}" for lv in levels) +
          "\n  NOTE the gap widens with level (+2 at 5, +15 at 60), so win rates are only "
          "comparable WITHIN a level, never across them.\n")
    print("WIN RATE")

    results = {}
    for slug, display in roster:
        row = {}
        for level in levels:
            wins, turns, left, worn = 0, [], [], 0
            for i in range(args.fights):
                char = Character("Sim", display, level)
                worn = dress(char, gen, level)
                won, t, hp = fight(char, ENEMY_MIX[i % len(ENEMY_MIX)], enemy_level(level, args.above), gen, rng)
                wins += won
                if won:
                    turns.append(t)
                    left.append(hp)
            row[level] = {
                "win": wins / args.fights,
                "turns": statistics.mean(turns) if turns else None,
                "left": statistics.mean(left) if left else None,
                "worn": worn,
            }
        results[slug] = (display, row)
        line = f"  {display:<14}"
        for level in levels:
            r = row[level]
            line += f"{r['win']*100:>4.0f}% "
        print(line + f"   (gear {row[levels[-1]]['worn']}/{len(GEAR_SLOTS)})")

    print("\n  " + " " * 14 + "".join(f"lv{l:<4}" for l in levels))
    print("\nTURNS TO KILL (won fights only)")
    for slug, (display, row) in results.items():
        line = f"  {display:<14}"
        for level in levels:
            t = row[level]["turns"]
            line += f"{t:>5.1f}" if t else "    -"
        print(line)

    print("\nHEALTH LEFT AFTER WINNING")
    for slug, (display, row) in results.items():
        line = f"  {display:<14}"
        for level in levels:
            h = row[level]["left"]
            line += f"{h*100:>5.0f}" if h is not None else "    -"
        print(line)

    # ---- the two numbers that explain most of the spread above
    print("\nMITIGATION, which is where most of the spread comes from")
    print(f"  {'class':<14}{'armor':>7}{'physical reduced':>18}{'magic reduced':>15}")
    for slug, (display, _row) in results.items():
        c = Character("Probe", display, levels[-1])
        dress(c, gen, levels[-1])
        print(f"  {display:<14}{c.armor:>7}{c.get_physical_reduction_percent():>17.0f}%"
              f"{c.get_magic_reduction_percent():>14.0f}%")
    print(f"  Character.MITIGATION_CONSTANT is {Character.MITIGATION_CONSTANT}, flat - it does not "
          f"scale with\n  level or attacker, so armour climbs with gear forever while magic "
          f"resistance stays at zero.")

    # ---- outliers, measured against the spread rather than an invented target
    print("\nOUTLIERS")
    # JUDGE EACH LEVEL AGAINST ITS OWN MEDIAN, NEVER AGAINST A FIXED BAR.
    #
    # Two things were wrong here and together they manufactured a crisis.
    #
    # The wording claimed a class "cannot reliably beat its own level" when
    # the benchmark is deliberately ABOVE the player's level - see --above,
    # whose own comment explains that a same-level fight reads 100% for
    # everyone and separates nothing. Nobody fought their own level.
    #
    # And the gap is a PERCENTAGE, so the benchmark gets harder as the run
    # goes up: +2 levels at level 5, +5 at 20, +15 at 60. A fixed <50% bar
    # therefore means something different at every level, and the output
    # read as every caster collapsing from level 40 - Mage, Priest, Shaman,
    # Paladin, Runemaster, Stormbringer all at 0% - when what actually
    # changed was the difficulty of the test. enemy_level's own docstring
    # says "A FIXED LEVEL GAP IS NOT A FIXED DIFFICULTY"; a fixed percentage
    # is not either, and acting on that table would have meant "fixing"
    # eight classes that are fine.
    #
    # So: the only honest comparison is between classes at the SAME level,
    # which is the median test. The absolute bar is gone, and the header
    # now states the real enemy level so the numbers cannot be misread.
    problems = []
    for level in levels:
        wr = {d: row[level]["win"] for _s, (d, row) in results.items()}
        median = statistics.median(wr.values())
        foe = enemy_level(level, args.above)
        for d, w in sorted(wr.items(), key=lambda kv: kv[1]):
            if median - w > 0.3:
                problems.append(f"level {level} vs level {foe}: {d} wins {w*100:.0f}% "
                                f"against a median of {median*100:.0f}%")
            elif w == 0 and median >= 0.3:
                problems.append(f"level {level} vs level {foe}: {d} wins NOTHING while the "
                                f"median is {median*100:.0f}%")
        tk = {d: row[level]["turns"] for _s, (d, row) in results.items()
              if row[level]["turns"]}
        if len(tk) > 3:
            med = statistics.median(tk.values())
            for d, t in tk.items():
                if t < med * 0.55:
                    problems.append(f"level {level}: {d} kills in {t:.1f} turns against a "
                                    f"median of {med:.1f} - far ahead")
                elif t > med * 1.8:
                    problems.append(f"level {level}: {d} needs {t:.1f} turns against a median "
                                    f"of {med:.1f} - far behind")
    if problems:
        for p in problems:
            print(f"  - {p}")
    else:
        print("  none - every class is inside the spread at every level sampled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
