#!/usr/bin/env python3
"""The bench holds two.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_bench_cap.py

Kyle, 16 Nov 2026, with nine people on his bench: "no limit to how many people i can bench??? Lol", then "I want a hard
cap of TWO benched characters." Checks, through the real party and the real recruit screen:
  1. a full party takes two more onto the bench, and then nobody;
  2. an active member can't be benched onto a full bench;
  3. the recruit screen says why and won't recruit anyone while there's no room, and does once there is;
  4. a save from before the cap keeps everyone it had (nobody is thrown away), and takes no one new.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
import pygame  # noqa: E402


def main():
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from entities.character import Character
    from entities.party import Party, MAX_BENCH, MAX_PARTY_SIZE
    bad = []
    hero = Character("Hero", "Warrior", 40)
    party = Party(hero)
    got = [party.add_member(Character(f"R{i}", "Priest", 40)) for i in range(MAX_PARTY_SIZE - 1 + MAX_BENCH + 2)]
    want = ["active"] * (MAX_PARTY_SIZE - 1) + ["bench"] * MAX_BENCH + [None, None]
    if got != want:
        bad.append(f"joining past the cap gave {got}")
    if len(party.bench) != MAX_BENCH:
        bad.append(f"the bench holds {len(party.bench)}")
    if party.bench_member(party.members[1]):
        bad.append("an active member went onto a full bench")

    # the recruit screen
    from core.game_state import GameStateManager
    from ui.screens.recruit_dialog_screen import RecruitDialogScreen
    from world.recruit_manager import get_recruit_manager
    sm = GameStateManager(pygame.display.get_surface())
    sm.player = hero
    sm.get_party = lambda: party
    rm = get_recruit_manager()
    rec = next(r for r in rm.recruits.values() if not rm.block_reason(r, 40) and not rm.is_recruited(r.recruit_id))
    scr = RecruitDialogScreen(sm, rec)
    scr.bond = None
    reason = scr.block_reason
    if not reason or "bench" not in reason:
        bad.append(f"the recruit screen gives no reason when there's no room ({reason!r})")
    scr._do_recruit()
    if scr.joined or any(getattr(m, "recruit_id", None) == rec.recruit_id for m in party.all_recruits()):
        bad.append("the recruit screen recruited someone with no room")
    party.remove_member(party.bench[0])
    if scr.block_reason:
        bad.append(f"still blocked with a bench seat free: {scr.block_reason}")

    # an old save over the cap
    big = Party(Character("Old", "Mage", 60))
    for i in range(MAX_PARTY_SIZE - 1 + 9):
        big.bench.append(Character(f"B{i}", "Mage", 60)) if i >= MAX_PARTY_SIZE - 1 else big.add_member(
            Character(f"A{i}", "Mage", 60))
    back = Party.from_dict(big.to_dict(), big.player)
    if len(back.bench) != 9:
        bad.append(f"an old save's bench of 9 loaded as {len(back.bench)}")
    if back.add_member(Character("New", "Mage", 60)) is not None:
        bad.append("an over-full old bench took someone new")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print(f"PASS - the bench holds {MAX_BENCH}; nobody joins past it, and nobody already on it is lost")
    return 0


if __name__ == "__main__":
    sys.exit(main())
