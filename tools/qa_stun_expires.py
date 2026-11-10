"""A stun must end. Every stun in the game was permanent.

THE BUG THIS EXISTS FOR (Kyle, 10 Nov 2026, relaying his friend): two-man
party in the Sunken Grotto of the Deep, druid tank and a healer, final boss.
"Every time it went to his druid it forced skip his turn ... Riptide Hex he
said is still in his stats." He was not being re-stunned. He was stunned
ONCE, forever.

Riptide Hex is a ONE-TURN stun riding a 4-cooldown hit. The deadlock:

    stunned            -> TurnMeter.update froze the meter, so no turn
    no turn            -> CombatEngine._end_turn never ran on them, and that
                          is the only thing that calls tick_status_effects
    no tick            -> the stun's duration never decremented
    duration unchanged -> still stunned, forever

Measured before the fix: a 1-turn stun still at duration 1 after the other
side had taken 285 turns. In a two-man party that is an unwinnable fight,
and nothing in the log ever said why the turn kept vanishing.

The fix is that a stunned combatant STILL FILLS THEIR METER and spends the
turn being stunned - the duration is counted in turns, so the turn has to
happen. These tests drive the real CombatEngine rather than inspecting
flags, because every flag involved was individually correct.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from combat.combat_engine import CombatEngine
from combat.status_effects import StatusEffect, EffectType
from entities.character import Character
from entities.monster import Monster
from entities.party import Party

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        failures.append(label)


def stun_effect(turns, name="Riptide Hex"):
    # real_time_seconds=None is NOT optional here: left unset, a BUFF/DEBUFF
    # defaults to BUFF_DURATION_SECONDS (1800) and is treated as a 30-minute
    # raid buff that tick_status_effects deliberately skips, so it would
    # never count down by turns and the test would "reproduce" a bug of its
    # own making. entities/monster.py builds every rider debuff with
    # real_time_seconds=None, and this has to match it.
    return StatusEffect("riptide_hex", name, EffectType.DEBUFF, turns,
                        stat_mods={"agility": -14}, is_stun=True,
                        real_time_seconds=None,
                        # The boss cast it, not the victim. This decides
                        # whether the effect gets the "landed this turn"
                        # grace turn - see apply_status_effect.
                        source_name="Naga Shrine Guardian")


def build_fight(hero_level=24):
    hero = Character(name="Bear", char_class="Druid", level=hero_level)
    party = Party(hero)
    boss = Monster("Naga Shrine Guardian", "humanoid_warrior", level=hero_level + 2)
    # Nobody dies: the fight must not end while turns are being counted.
    boss.current_health = boss.max_health = 999999
    hero.health = hero.current_health = 999999
    engine = CombatEngine(hero, boss, party=party, enemies=[boss])
    return hero, boss, engine


def spin(engine, hero, boss, frames=4000, until=None):
    """Drive the fight.

    OUTSIDE THE COMBAT SCREEN NOTHING PERFORMS A MONSTER'S TURN. The engine
    picks an actor and then waits for someone to act with it, so a headless
    harness stalls on the boss forever and the hero never gets another turn -
    which looks exactly like the stun bug and is not it. This passes on any
    turn that is not the hero's, so the only thing being measured is what
    happens to the hero's.

    The hero's STUNNED turns are consumed by CombatEngine.update itself -
    that is the behaviour under test, so this must never consume them.
    """
    stunned_turns = 0
    for _ in range(frames):
        before = len(engine.combat_log)
        engine.update(0.05)
        for msg in engine.combat_log[before:]:
            if "is stunned and loses the turn" in msg and hero.name in msg:
                stunned_turns += 1
        actor = engine.current_actor
        if actor is not None and actor is not hero:
            engine._end_turn(actor)
            engine.current_actor = None
        if until is not None and until():
            break
    return stunned_turns


def hero_turns(engine, hero, boss, want, frames=20000):
    """Count live turns actually handed to the hero (consuming each)."""
    taken = 0
    for _ in range(frames):
        engine.update(0.05)
        actor = engine.current_actor
        if actor is None:
            continue
        if actor is hero:
            taken += 1
        engine._end_turn(actor)
        engine.current_actor = None
        if taken >= want:
            break
    return taken


print("== a stunned combatant still accrues turn meter")
hero, boss, engine = build_fight()
hero.apply_status_effect(stun_effect(1))
start = hero.turn_meter
spin(engine, hero, boss, frames=400)
check("the meter moves while stunned", hero.turn_meter > start or not hero.is_stunned,
      "meter frozen - this is the deadlock, the stun can never tick down")

print("\n== THE REPORTED BUG: a 1-turn stun ends after one lost turn")
hero, boss, engine = build_fight()
hero.apply_status_effect(stun_effect(1))
spin(engine, hero, boss, until=lambda: not hero.is_stunned)
check("the stun wears off", not hero.is_stunned,
      f"still stunned; Riptide Hex duration never reached 0")
check("the druid is no longer in the stat panel carrying it",
      not any(e.name == "Riptide Hex" for e in hero._effects()))

print("\n== the log says why the turn was lost")
hero, boss, engine = build_fight()
hero.apply_status_effect(stun_effect(1))
spin(engine, hero, boss, until=lambda: not hero.is_stunned)
said = [m for m in engine.combat_log if "stunned" in m.lower() and hero.name in m]
check("a stunned turn is announced", said,
      "the turn vanishes silently, which is what made this read as a broken game")

print("\n== a longer stun costs exactly as many turns as it says")
for turns in (1, 2, 3):
    hero, boss, engine = build_fight()
    hero.apply_status_effect(stun_effect(turns))
    lost = spin(engine, hero, boss, until=lambda: not hero.is_stunned)
    check(f"a {turns}-turn stun costs {turns} turn(s)", lost == turns,
          f"lost {lost}")

print("\n== the stun works at all: the turn IS taken from them")
hero, boss, engine = build_fight()
hero.apply_status_effect(stun_effect(2))
acted_while_stunned = False


def _caught():
    global acted_while_stunned
    if engine.current_actor is hero and hero.is_stunned:
        acted_while_stunned = True
        return True
    return not hero.is_stunned


spin(engine, hero, boss, until=_caught)
check("a stunned combatant is never handed a live turn", not acted_while_stunned,
      "the stun is being skipped over entirely - it no longer does anything")

print("\n== a monster eats a stun the same way (one rule, not two)")
hero, boss, engine = build_fight()
boss.apply_status_effect(stun_effect(1, "Bash"))
# The BOSS is the stunned one here, so this drive consumes the HERO's
# turns and leaves the boss's stunned turns to the engine.
spin(engine, boss, hero, until=lambda: not boss.is_stunned)
check("a stunned boss recovers too", not boss.is_stunned,
      "monsters are on a separate code path again")

print("\n== an unstunned fight is untouched")
hero, boss, engine = build_fight()
turns = hero_turns(engine, hero, boss, 5)
check("a clean combatant still takes turns normally", turns == 5, f"got {turns}")
check("nothing was logged as stunned",
      not any("stunned" in m.lower() for m in engine.combat_log))

print()
if failures:
    print(f"FAILED ({len(failures)}): " + ", ".join(failures))
    sys.exit(1)
print("All stun expiry checks passed.")
