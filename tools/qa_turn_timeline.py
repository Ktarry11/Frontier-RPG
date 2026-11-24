#!/usr/bin/env python3
"""The turn timeline tells the truth (docs/turn_timeline_design.md).

    PYTHONPATH=. python3 tools/qa_turn_timeline.py

Kyle, 20 Nov 2026: the bar down the right of combat shows who moves next, and hovering a spell shows where its caster
lands, "so we can plan". A plan is only as good as the bar, so this runs fights on the real TurnMeter and checks:

  1. ORDER: before every turn, whoever the timeline puts lowest is who actually acts next.
  2. THE GHOST: after a cast of any speed, the caster lands exactly where time_after_cast() said they would.
  3. HASTE: a hasted combatant's next turn comes sooner on the bar, by the haste.
  4. THE SPEED PASS: every class's castable abilities carry one of instant, short, medium and long, with at least
     one short and one long, and nothing that hurts an enemy instant without a 2-turn cooldown (Kyle, 23 Nov 2026)
     (tools/build_cast_speeds.py --check).
"""
import os
import random
import subprocess
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TURN_THRESHOLD  # noqa: E402


def fight(seed):
    from entities.character import Character
    from entities.monster import Monster
    from combat.turn_meter import TurnMeter
    random.seed(seed)
    people = [Character(n, c, 40) for n, c in (("Kyle", "Shaman"), ("Rhodri", "Knight of Xoroth"),
                                               ("Yiannis", "Paladin"), ("Leif", "Primalist"))]
    foes = [Monster("Mangy Wolf", "beast_basic", 40), Monster("Defias Thug", "humanoid_warrior", 41),
            Monster("Defias Pillager", "humanoid_caster", 39)]
    return TurnMeter(people + foes), people, foes


def main():
    problems = []
    turns = ghosts = 0
    for seed in range(6):
        tm, people, foes = fight(seed)
        for _ in range(60):
            line = sorted(tm.timeline(), key=lambda t: t[1])
            predicted = line[0][0]
            acted = None
            for _tick in range(20000):
                acted = tm.update(0.0005)
                if acted is not None:
                    break
            if acted is None:
                problems.append(f"seed {seed}: nobody acted")
                break
            turns += 1
            if acted is not predicted:
                gap = abs(tm.time_to_turn(predicted) - tm.time_to_turn(acted)) if predicted.is_alive() else 1
                if gap > 0.002:         # a dead heat inside one tick can go either way
                    problems.append(f"seed {seed}: the bar said {predicted.name} moves next, {acted.name} did")
            speed = random.choice((0.25, 0.5, 0.75, 1.0))   # instant, short, medium, long
            want = tm.time_after_cast(acted, speed)
            tm.consume_turn(acted, speed)
            got = tm.time_to_turn(acted)
            ghosts += 1
            if abs(got - want) > 1e-6:
                problems.append(f"seed {seed}: {acted.name}'s ghost said {want:.4f}, landed {got:.4f}")
    # haste moves the ghost up: 50% haste should make the same wait two thirds as long
    tm, people, _ = fight(99)
    who = people[0]
    who.turn_meter = 0
    slow = tm.time_after_cast(who, 1.0)
    fast = tm.time_after_cast(who, 1.0, extra_haste=50)
    own = getattr(who, "haste", 0) or 0
    want = slow * (100 + own) / (100 + own + 50)
    if abs(fast - want) > 1e-6:
        problems.append(f"haste: a 50% haste ghost landed at {fast:.4f}, wanted {want:.4f}")
    # the scale: every next turn after a normal cast fits on the bar
    tm, people, foes = fight(7)
    for c in people + foes:
        c.turn_meter = 0
    if max(p for _, p in tm.timeline()) > 1.0 + 1e-6:
        problems.append("scale: a normal turn from empty doesn't fit on the bar")
    r = subprocess.run([sys.executable, "tools/build_cast_speeds.py", "--check"], capture_output=True, text=True)
    if r.returncode:
        problems.append("speed pass: " + r.stdout.strip().splitlines()[-1])
    for p in problems[:20]:
        print("  -", p)
    if problems:
        print(f"{len(problems)} problem(s)")
        return 1
    print(f"turn timeline OK - {turns} turns predicted right, {ghosts} ghosts landed where shown, haste and scale "
          f"hold, and every class has its speeds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
