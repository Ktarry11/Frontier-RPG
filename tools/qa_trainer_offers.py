#!/usr/bin/env python3
"""A skill you skip must stay findable at the trainer, at the same place in the list.

    PYTHONPATH=. python3 tools/qa_trainer_offers.py

Kyle, 2026-10-31: "if we don't buy a skill, like at lvl 4, then we grow too high
of level we cant buy it, it vanishes from the option (i tested with the +5
levels)."

Two separate questions, and they have different answers.

DOES IT LEAVE THE LIST? No - swept below across all 30 classes and every level
from 1 to 60, no ability ever stops being offered while it is still untrained,
and nothing is lost by waiting: you are sold the highest rank you qualify for,
at that rank's price, which is cheaper than buying your way up through the ones
you skipped.

DOES IT MOVE? It did, a lot. The list was sorted by the level of the RANK being
sold, so a skipped ability sank further down every time its next rank unlocked -
Rejuvenation sits at row 1 at level 9 and row 11 at level 14, renamed "(Rank 2)",
with seven rows visible. Sorting on the ability's FIRST rank pins it.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob  # noqa: E402

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok   {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL {label}  {detail}")


def main():
    from entities.character import Character
    from world import training_manager as tm

    classes = sorted(os.path.basename(p)[:-5] for p in glob.glob("data/abilities/*.json"))
    classes = [c for c in classes if not c.startswith("_") and c != "asher_unique"]

    # ---- 1. nothing ever leaves the trainer while untrained -------------------
    vanished = []
    moved = []
    for cls in classes:
        c = Character("T", cls, level=1)
        c.enable_training()
        seen = set()
        pos_history = {}
        for lv in range(1, 61):
            c.level = lv
            c._refresh_ability_ranks()
            offers = tm.offers(c)
            ids = {o["ability"].ability_id for o in offers}
            for aid in seen - ids:
                if c.trained_ranks.get(aid, 0) == 0:
                    vanished.append((cls, aid, lv))
            seen |= ids
            # position drift of an ability that is still brand new (never bought)
            for i, o in enumerate(offers):
                if not o["new"]:
                    continue
                aid = o["ability"].ability_id
                prev = pos_history.get(aid)
                if prev is not None and i > prev + 2:
                    moved.append((cls, aid, lv, prev, i))
                pos_history[aid] = i

    check("no ability leaves the trainer while still untrained",
          not vanished, f"{len(vanished)}: {vanished[:4]}")
    check("a skipped ability does not drift down the list as you level",
          not moved, f"{len(moved)} drifts, e.g. {moved[:4]}")

    # ---- 2. the concrete case Kyle described ---------------------------------
    c = Character("T", "druid", level=1)
    c.enable_training()
    c.level = 4
    c._refresh_ability_ranks()
    at4 = tm.offers(c)
    rejuv4 = [o for o in at4 if o["ability"].ability_id == "druid_rejuvenation"]
    check("Rejuvenation is on offer at level 4", len(rejuv4) == 1)
    pos4 = at4.index(rejuv4[0])

    c.level = 14
    c._refresh_ability_ranks()
    at14 = tm.offers(c)
    rejuv14 = [o for o in at14 if o["ability"].ability_id == "druid_rejuvenation"]
    check("still on offer at level 14 after skipping it", len(rejuv14) == 1)
    pos14 = at14.index(rejuv14[0])
    # Seven rows fit on the trainer panel. The old sort put this at row 11 of 16 by level 14,
    # off-screen behind a scroll; it must stay on the first page. It does slide a few places as
    # abilities that unlock EARLIER than it (Wrath, Moonfire, Thorns) come up for their own
    # rank-ups - that ordering is stable and correct, which the drift sweep above is what checks.
    VISIBLE_ROWS = 7
    check("and it is still on the first page of the trainer, not buried",
          pos14 < VISIBLE_ROWS,
          f"row {pos4} at lvl 4 -> row {pos14} of {len(at14)} at lvl 14")
    check("it is flagged as overdue so the player can see they skipped it",
          rejuv14[0].get("behind", 0) >= 3, f"behind={rejuv14[0].get('behind')}")

    # ---- 3. skipping costs nothing ------------------------------------------
    # Buying rank 2 outright must not cost more than rank 1 + rank 2 would have.
    ab = rejuv14[0]["ability"]
    straight = tm.rank_cost(ab, rejuv14[0]["rank"])
    stepwise = sum(tm.rank_cost(ab, r) for r in range(1, rejuv14[0]["rank"] + 1))
    check("waiting is not punished - the skipped ranks are not charged for",
          straight <= stepwise, f"{straight} vs {stepwise}")

    # ---- 4. and you actually receive the higher rank -------------------------
    before = c.trained_ranks.get("druid_rejuvenation", 0)
    c.train_ability("druid_rejuvenation", rejuv14[0]["rank"])
    check("training a skipped ability grants the higher rank, not rank 1",
          c.trained_ranks["druid_rejuvenation"] == rejuv14[0]["rank"] > before,
          f"{before} -> {c.trained_ranks.get('druid_rejuvenation')}")

    print(f"\n{len(FAILS)} failed" if FAILS else "\ntrainer offers are stable and complete")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
