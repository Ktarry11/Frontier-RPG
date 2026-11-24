#!/usr/bin/env python3
"""Nothing can be stunned turn after turn: stuns diminish.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_stun_diminishing.py

Kyle, 16 Nov 2026: "enemies STILL get stun locked bro" (a level 56 boss held by Frostbite turn after turn). With a
two-turn stun thrown at the target every single one of its turns, for 20 turns:
  1. a boss is never stunned at all (23 Nov 2026, a friend's playtest Kyle passed on: "Bosses should be immune to
     stuns"; it was one turn in four);
  2. anything else is stunned on at most two turns in five, and never three turns running;
  3. anything else is still stunned at all (the rule cuts stun-lock, not stuns).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def pattern(monster):
    from combat.status_effects import StatusEffect, EffectType
    out = ""
    for _turn in range(20):
        stun = StatusEffect("qa_stun", "Frostbite", EffectType.DEBUFF, 2, is_stun=True, source_name="Mage",
                            real_time_seconds=None)
        monster.apply_status_effect(stun)
        out += "S" if monster.is_stunned else "."
        list(monster.tick_status_effects() or [])
    return out


def main():
    from entities.monster import Monster
    bad = []
    boss = Monster("Tunnel-King Ruzzak", "beast_basic", level=56)
    boss.is_boss = True
    mob = Monster("Mangy Wolf", "beast_basic", level=56)
    mob.is_boss = False
    pb, pm = pattern(boss), pattern(mob)
    print(f"boss: {pb}\nmob:  {pm}")
    if "S" in pb:
        bad.append("a boss was stunned; bosses are immune to stuns")
    if "SSS" in pm:
        bad.append("a mob was stunned three turns running")
    if any(pm[i:i + 5].count("S") > 2 for i in range(len(pm) - 4)):
        bad.append("a mob was stunned more than twice in five turns")
    if "S" not in pm:
        bad.append("stuns stopped landing on ordinary enemies")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - bosses shrug off stuns, and nothing else can be held turn after turn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
