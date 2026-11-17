#!/usr/bin/env python3
"""Every way a trade gets learned leaves it at skill 1, never 0.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_professions_start_at_one.py

Kyle, 16 Nov 2026: "ensure WE START PROFESSIONS AT LVL 1 AND NOT LVL 0!!! when we learn it". The trainer path already
did (Character.learn_profession, 14 Nov), but the test menu's Learn All Professions skipped that rule and left every
trade at 0, so nothing could be bought or crafted.

  1. The trainer (profession_manager.learn) and Character.learn_profession: skill 1.
  2. The test menu's Learn All Professions: every trade at 1 or more, none at 0.
  3. A save from before the fix, with a known trade at 0, loads at 1.
  4. Unlearning then relearning starts at 1 again.
  5. A trade that already had skill keeps it (learning never lowers skill).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from entities.character import Character  # noqa: E402
from world import profession_manager as pm  # noqa: E402
from world import testing  # noqa: E402

BAD = []


def check(label, cond, detail=""):
    print(f"  {'ok  ' if cond else 'FAIL'} {label}" + (f"  {detail}" if not cond and detail else ""))
    if not cond:
        BAD.append(label)


def hero():
    return Character(name="Tester", char_class="Warrior", level=20)


def main():
    profs = list(pm.professions())

    c = hero()
    first = profs[0]
    check("learn_profession starts at 1", c.learn_profession(first) and c.profession_skills.get(first) == 1,
          str(c.profession_skills.get(first)))

    class _Party:
        copper = 10 ** 9

        def remove_currency(self, n):
            self.copper -= n
            return True

    c = hero()
    ok, msg = pm.learn(c, _Party(), first)
    check("the trainer starts it at 1", ok and c.profession_skills.get(first) == 1,
          f"{ok} {msg} {c.profession_skills.get(first)}")

    c = hero()
    testing.learn_all_professions(c)
    zero = [p for p in c.known_professions if c.profession_skills.get(p, 0) < 1]
    check(f"Learn All Professions leaves none at 0 ({len(c.known_professions)} trades)", not zero, str(zero))

    c = hero()
    c.learn_profession(first)
    data = c.to_dict()
    data["profession_skills"][first] = 0
    back = Character.from_dict(data)
    check("an old save with a known trade at 0 loads at 1", back.profession_skills.get(first) == 1,
          str(back.profession_skills.get(first)))

    c = hero()
    c.learn_profession(first)
    c.unlearn_profession(first)
    c.learn_profession(first)
    check("relearning starts at 1 again", c.profession_skills.get(first) == 1, str(c.profession_skills.get(first)))

    c = hero()
    c.profession_skills[first] = 42
    c.learn_profession(first)
    check("learning never lowers skill already earned", c.profession_skills.get(first) == 42,
          str(c.profession_skills.get(first)))

    print("PASS" if not BAD else f"FAILED: {BAD}")
    return 0 if not BAD else 1


if __name__ == "__main__":
    sys.exit(main())
