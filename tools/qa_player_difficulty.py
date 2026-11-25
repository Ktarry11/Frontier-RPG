#!/usr/bin/env python3
"""The player's own Difficulty settings (world/player_difficulty.py, 25 Nov 2026).

    PYTHONPATH=. python3 tools/qa_player_difficulty.py

Kyle, 25 Nov 2026: "a small box where the EXP bar is, that opens a new menu. We can call it 'Difficulty'... 'Open
World' 'Dungeons' 'Skull Zones' 'Frontier Zones' -- They can adjust either HP or Damage... 0.5x to 2x. HP and damage
done seperately and all 4 zones done seperately." This holds:
  1  at 1x everywhere, and with no party bound (every sim and balance tool), the game's own numbers are untouched
  2  every hidden kind lands in its tab: one-skull kinds under Skull Zones, two-skull kinds under Frontier Zones
  3  a dungeon boss and a dungeon's trash count as Dungeons; an open-world creature counts as Open World
  4  a setting scales exactly the category and the stat it names, and a made creature takes new health at its fight
  5  the save keeps it, and a bad or missing value loads as 1x
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


class _M:
    is_boss = False
    level = 30


def findings():
    from world import player_difficulty as pd
    from world import difficulty as D
    from world.hidden_zones import creature_kinds
    bad = []
    was = pd._PARTY

    class _Party:
        pass

    party = _Party()
    party.difficulty = pd.fresh()

    def mk(name, zone=None, boss=False, where="open_zone"):
        m = _M()
        m.name, m.is_boss, m.spawn_zone, m.location_type = name, boss, zone, where
        return m

    boss = next(iter(D.dungeon_bosses()))
    samples = [mk("Mottled Boar", "Durotar"), mk(boss, boss=True), mk("Mottled Boar", "Ragefire Chasm", where="cave")]

    # 1
    pd.bind(None)
    unbound = [(D.factor(m, "health"), D.factor(m, "damage")) for m in samples]
    pd.bind(party)
    at_one = [(D.factor(m, "health"), D.factor(m, "damage")) for m in samples]
    if unbound != at_one:
        bad.append("difficulty: 1x everywhere changes the game's own numbers")

    # 2
    want = {"hidden_layer": "skull", "skull_zone": "skull", "frontier_deep": "frontier", "frontier_open": "frontier"}
    for name, kind in creature_kinds().items():
        got = pd.category(mk(name))
        if want.get(kind) != got:
            bad.append(f"difficulty: a {kind} creature counts as {got}")
            break

    # 3
    for m, cat in zip(samples, ("open", "dungeon", "dungeon")):
        if pd.category(m) != cat:
            bad.append(f"difficulty: {m.name} in {m.spawn_zone} counts as {pd.category(m)}, not {cat}")

    # 4
    for m in samples:
        cat = pd.category(m)
        for what in ("health", "damage"):
            pd.reset(party)
            base = D.factor(m, what)
            pd.set_step(party, cat, what, 1.75)
            if abs(D.factor(m, what) - base * 1.75) > 1e-6:
                bad.append(f"difficulty: {cat} {what} at 1.75x doesn't scale by 1.75")
            other = "damage" if what == "health" else "health"
            pd.reset(party)
            base_other = D.factor(m, other)
            pd.set_step(party, cat, what, 1.75)
            if abs(D.factor(m, other) - base_other) > 1e-6:
                bad.append(f"difficulty: {cat} {what} also moved {other}")
            for c2, _t in pd.CATEGORIES:
                if c2 != cat:
                    pd.reset(party)
                    b2 = D.factor(m, what)
                    pd.set_step(party, c2, what, 2.0)
                    if abs(D.factor(m, what) - b2) > 1e-6:
                        bad.append(f"difficulty: the {c2} setting moved a {cat} creature")
    pd.reset(party)
    m = samples[0]
    m.max_health = m.current_health = 100
    m._difficulty_health, m._difficulty_kind = D.factor(m, "health"), D.kind_of(m)
    m.current_health = 50
    pd.set_step(party, "open", "health", 2.0)
    D.refresh_health(m)
    if m.max_health != 200 or m.current_health != 100:
        bad.append(f"difficulty: a made creature didn't take the new health at its fight ({m.current_health}/{m.max_health})")

    # 5
    saved = json.loads(json.dumps(party.difficulty))
    if pd.clean(saved) != party.difficulty:
        bad.append("difficulty: the save doesn't keep the settings")
    if pd.clean({"open": {"health": 3.0}, "dungeon": "junk"}) != pd.fresh() or pd.clean(None) != pd.fresh():
        bad.append("difficulty: a bad saved value doesn't load as 1x")
    pd.bind(was)
    return bad


def main():
    bad = findings()
    for b in bad:
        print("  FAIL", b)
    print("player difficulty " + ("FAILED" if bad else "OK - 1x is the game as tuned, each tab moves only its own "
                                                     "monsters and stat, and it saves"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
