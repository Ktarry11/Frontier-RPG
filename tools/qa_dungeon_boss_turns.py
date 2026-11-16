#!/usr/bin/env python3
"""No boss is a punching bag: not in a dungeon, not in a cave, not in the open world.

    PYTHONPATH=. python3 tools/qa_dungeon_boss_turns.py

Kyle, 16 Nov 2026: "screen through all dungeon bosses in the game to ensure none of them are buffing / debuffing /
punching bags". Fights every dungeon boss (a dungeon's, a tuned dungeon's, a hidden level's and a deep frontier's;
world/difficulty.kind_of) for 40 turns with tools/audit_boss_turns.assess and fails if any of them:
  - spends more than 30% of its turns on buffs, debuffs or heals that hurt nobody,
  - carries a buff or debuff it never gets to use (a dead slot), or
  - never throws anything dangerous (a big hit, a party blast, a stun with a hammer behind it, a killing DoT, a
    desperation move or adds).
Kyle, after the dungeon pass: "Yup, open world and caves next", so field bosses, caves' bosses (a cave that isn't a
dungeon counts as the open world), skull zones' and open frontiers' are held too. The fix is
tools/fix_dungeon_boss_turns.py, which is idempotent: run it after any builder rewrites a boss's kit.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)


def main():
    import audit_monster_combat as AMC
    import audit_boss_turns as ABT
    from fix_dungeon_boss_turns import dungeon_bosses, failing, DUNGEON_KINDS, OPEN_KINDS
    with contextlib.redirect_stdout(io.StringIO()):
        cm = AMC._manager()
    names = dungeon_bosses(cm, DUNGEON_KINDS | OPEN_KINDS)
    with contextlib.redirect_stdout(io.StringIO()):
        rows, skipped = ABT.assess(names, cm)
    bad = failing(rows)
    print(f"{len(names)} bosses fought (dungeons, caves and the open world), {ABT.TURNS} turns each")
    if bad or skipped:
        print(f"FAIL ({len(bad)} failing, {len(skipped)} could not be fought) - run tools/fix_dungeon_boss_turns.py")
        for r in bad:
            print(f"  - {r['name']} ({r['kind']}, lvl {r['level']}): passive {r['passive']:.0%}, "
                  f"dangers {', '.join(r['dangers']) or 'none'}, dead {r['dead'] or 'none'}")
        for n, why in skipped:
            print(f"  - {n}: {why}")
        return 1
    print("PASS - every boss acts, uses what it carries, and has something dangerous")
    return 0


if __name__ == "__main__":
    sys.exit(main())
