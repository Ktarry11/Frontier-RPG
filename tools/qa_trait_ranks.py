#!/usr/bin/env python3
"""A companion's own traits rank up at 1, 15, 30, 45 and 60, and keep their rank through a save.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_trait_ranks.py

Kyle, 16 Nov 2026, looking at a level 60 companion's "Where the Strikes Land, Rank 1/5": "Character traits not leveling
up...should be 1, 15, 30, 45, and 60." The kit is put back on every load and on recruiting, after the character's
ranks were refreshed, so every trait sat at Rank 1 until a level-up that a level 60 never gets.

For every companion with a ranked trait, built at 15, 30, 45 and 60 and then saved and loaded: each ranked trait is
at the rank its level has earned.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    from entities.character import Character
    from world.recruit_manager import get_recruit_manager
    with contextlib.redirect_stdout(io.StringIO()):
        rm = get_recruit_manager()
    bad, checked = [], 0
    for rid, r in rm.recruits.items():
        for lv in (15, 30, 45, 60):
            with contextlib.redirect_stdout(io.StringIO()):
                c = r.build_character(lv)
                c.level = lv
                c._refresh_ability_ranks()
                again = Character.from_dict(c.to_dict())
            for ch, how in ((c, "built"), (again, "after a load")):
                for a in ch.ability_book.get_all_abilities():
                    if not a.ability_id.startswith("personal_") or len(a.ranks) < 2:
                        continue
                    want = max(i for i, rk in enumerate(a.ranks) if rk["level_req"] <= ch.level) + 1
                    checked += 1
                    if a.current_rank_index + 1 != want:
                        bad.append(f"{rid} level {ch.level} {how}: {a.name} at Rank {a.current_rank_index + 1}, "
                                   f"earned Rank {want}")
    print(f"{checked} ranked traits checked")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("PASS - every companion's traits rank up at 1, 15, 30, 45 and 60, and keep it through a load")
    return 0


if __name__ == "__main__":
    sys.exit(main())
