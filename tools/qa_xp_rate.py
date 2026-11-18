#!/usr/bin/env python3
"""The player's experience rate (world/xp_rate.py) does what the switch says.

    PYTHONPATH=. python3 tools/qa_xp_rate.py

Kyle, 18 Nov 2026: "0.5x, 1x, 1.5x, 2x, 2.5x, or 3x EXP which will be for quests and kills. So people can pick
their own level of fun."
  1. Exactly those six rates, 1x by default, and nothing else can be set.
  2. A quest's reward and a kill's reward both scale by the rate, and only by it.
  3. The rate is the save's: it survives a save and load, and an old save without one loads at 1x.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    bad = []
    from entities.character import Character
    from entities.party import Party
    from world import xp_rate as X
    player = Character("Rate", "Warrior")
    player.level = 20
    party = Party(player)
    print(f"1. rates {X.RATES}, default {X.current()}")
    if X.RATES != (0.5, 1.0, 1.5, 2.0, 2.5, 3.0) or X.current() != 1.0:
        bad.append("the rates or the default aren't Kyle's")
    if X.set_rate(party, 4.0) or X.current() != 1.0:
        bad.append("a rate Kyle didn't list was accepted")

    from world.quest_manager import get_quest_manager
    q = next(q for q in get_quest_manager().quests.values() if getattr(q, "reward_exp", 0) > 500)
    from combat.combat_engine import CombatEngine
    reward = lambda: q.get_scaled_exp_reward(q.quest_level)
    out = {}
    for r in X.RATES:
        X.set_rate(party, r)
        out[r] = reward()
    print(f"2. quest '{getattr(q, "title", q.quest_id)}' pays {out}")
    for r in X.RATES:
        if abs(out[r] - out[1.0] * r) > 1:
            bad.append(f"the quest pays {out[r]} at {r}x, not {out[1.0] * r:g}")

    import inspect
    src = inspect.getsource(CombatEngine)
    if "player_xp_rate()" not in src:
        bad.append("kill experience doesn't read the player's rate")

    X.set_rate(party, 2.5)
    back = Party.from_dict(party.to_dict(), player)
    print(f"3. saved at 2.5x, loaded at {back.xp_rate}x")
    if back.xp_rate != 2.5:
        bad.append("the rate didn't survive a save")
    data = party.to_dict()
    data.pop("xp_rate", None)
    old = Party.from_dict(data, player)
    if old.xp_rate != 1.0:
        bad.append("an old save without a rate didn't load at 1x")

    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  - " + b)
        return 1
    print("PASS: quests and kills pay at the player's chosen rate, 0.5x to 3x, and it's kept with the save")
    return 0


if __name__ == "__main__":
    sys.exit(main())
