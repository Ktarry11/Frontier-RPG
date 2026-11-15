#!/usr/bin/env python3
"""A save's trained ranks survive ranks being added to an ability.

    PYTHONPATH=. python3 tools/qa_trained_rank_migration.py

15 Nov 2026: tools/fix_ability_rank_levels.py filled the 16-level gaps in 50 abilities, so Execute went from
ranks at [24, 40] to [24, 32, 40, 52]. Trainers record what you bought by rank NUMBER, so an old save's
"Execute rank 2" (the level-40 rank) would have become the level-32 rank. Saves now carry the LEVEL of each
trained rank as well, and an old save is read through data/migrations/rank_levels_before.json.

  1. An old save (numbers only) keeps the rank it paid for: Execute rank 2 becomes rank 3, the level-40 rank.
  2. A new save writes trained_rank_levels and loads back to the same ranks.
  3. An ability nobody changed keeps its number.
"""
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main():
    from entities.character import Character
    bad = []
    old_levels = json.load(open("data/migrations/rank_levels_before.json", encoding="utf-8"))
    c = Character(name="Grom", char_class="Warrior", level=50)
    c.enable_training(grandfather=False)
    c.trained_ranks = {"warrior_execute": 2, "warrior_heroic_strike": 3}
    data = c.to_dict()
    data.pop("trained_rank_levels", None)          # a save from before 15 Nov
    old = Character.from_dict(data)
    ex = old.ability_book.get_ability("warrior_execute")
    n = old.trained_ranks.get("warrior_execute")
    want_level = old_levels["warrior_execute"][1]
    got_level = ex.ranks[n - 1]["level_req"] if n else None
    print(f"1. old save: Execute rank 2 (level {want_level} then) -> rank {n} (level {got_level} now)")
    if got_level != want_level:
        bad.append(f"an old save's Execute rank 2 became the level-{got_level} rank, not the level-{want_level} one")
    if "warrior_heroic_strike" not in old_levels and old.trained_ranks.get("warrior_heroic_strike") != 3:
        bad.append("Heroic Strike (unchanged) lost its rank number")
    print(f"3. an unchanged ability keeps its number: Heroic Strike rank {old.trained_ranks.get('warrior_heroic_strike')}")

    data2 = old.to_dict()
    if "trained_rank_levels" not in data2:
        bad.append("a new save doesn't write trained_rank_levels")
    again = Character.from_dict(json.loads(json.dumps(data2)))
    if again.trained_ranks != old.trained_ranks:
        bad.append(f"a new save loads back different ranks: {again.trained_ranks} vs {old.trained_ranks}")
    print(f"2. new save round-trips: {again.trained_ranks}")

    if bad:
        print("\nFAILED:")
        for b in bad:
            print("  -", b)
        return 1
    print("\ntrained ranks OK - a save keeps the ranks it paid for when ranks are added.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
